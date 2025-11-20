using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;
using ObjectDetectionCamera.Config;
using ObjectDetectionCamera.Yolo;

namespace ObjectDetectionCamera.Services;

public class OnnxYoloDetector : IDisposable
{
    private readonly InferenceSession _session;
    private readonly YoloOutputParser _parser;
    private readonly string _inputName;
    private readonly string _outputName;
    private readonly int _channelCount;
    private readonly int _inputWidth;
    private readonly int _inputHeight;
    private readonly bool _inputChannelFirst;
    private bool _disposed;

    public OnnxYoloDetector(string modelPath, string labelsPath)
    {
        if (!File.Exists(modelPath))
        {
            throw new FileNotFoundException($"Unable to locate model at {modelPath}", modelPath);
        }

        _session = new InferenceSession(modelPath);
        _parser = new YoloOutputParser(labelsPath);

        _channelCount = _parser.ChannelCount;

        _inputName = _session.InputMetadata.ContainsKey(AppConfig.InputName)
            ? AppConfig.InputName
            : _session.InputMetadata.Keys.First();

        _outputName = _session.OutputMetadata.ContainsKey(AppConfig.OutputName)
            ? AppConfig.OutputName
            : _session.OutputMetadata.Keys.First();

        var inputMeta = _session.InputMetadata[_inputName];
        var inputDims = inputMeta.Dimensions.ToArray();

        // Default to config values; override when model metadata provides explicit sizes.
        _inputHeight = inputDims.Length >= 3 && inputDims[^2] > 0 ? inputDims[^2] : AppConfig.InputHeight;
        _inputWidth = inputDims.Length >= 3 && inputDims[^1] > 0 ? inputDims[^1] : AppConfig.InputWidth;
        _inputChannelFirst = DetermineChannelFirst(inputDims);
    }

    public IList<YoloBoundingBox> Detect(Bitmap bitmap)
    {
        if (bitmap == null)
        {
            throw new ArgumentNullException(nameof(bitmap));
        }

        var (resized, scale, offsetX, offsetY) = ResizeWithLetterbox(bitmap);
        var tensor = ExtractTensor(resized);

        var inputValue = DisposableNamedOnnxValue.CreateFromTensor(_inputName, tensor);
        try
        {
            using IDisposableReadOnlyCollection<DisposableNamedOnnxValue> results = _session.Run(new[] { inputValue });
            var output = results.First(r => r.Name == _outputName);

            var tensorOutput = output.AsTensor<float>();
            bool channelFirst = IsChannelFirst(tensorOutput);
            var buffer = tensorOutput.ToArray();

            var boxes = _parser.ParseOutputs(
                buffer,
                channelFirst,
                AppConfig.ScoreThreshold,
                AppConfig.IoUThreshold,
                _inputWidth,
                _inputHeight);

            ProjectToOriginalFrame(boxes, scale, offsetX, offsetY, bitmap.Width, bitmap.Height);
            return boxes;
        }
        finally
        {
            (inputValue as IDisposable)?.Dispose();
            resized.Dispose();
        }
    }

    private (Bitmap resized, float scale, int offsetX, int offsetY) ResizeWithLetterbox(Bitmap source)
    {
        var resized = new Bitmap(_inputWidth, _inputHeight, PixelFormat.Format24bppRgb);

        var scale = Math.Min(
            _inputWidth / (float)source.Width,
            _inputHeight / (float)source.Height);

        var scaledWidth = (int)Math.Round(source.Width * scale);
        var scaledHeight = (int)Math.Round(source.Height * scale);
        var offsetX = (_inputWidth - scaledWidth) / 2;
        var offsetY = (_inputHeight - scaledHeight) / 2;

        using (var graphics = Graphics.FromImage(resized))
        {
            graphics.Clear(Color.Black);
            graphics.CompositingMode = System.Drawing.Drawing2D.CompositingMode.SourceCopy;
            graphics.CompositingQuality = System.Drawing.Drawing2D.CompositingQuality.HighQuality;
            graphics.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.Bilinear;
            graphics.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighQuality;
            graphics.DrawImage(source, offsetX, offsetY, scaledWidth, scaledHeight);
        }

        return (resized, scale, offsetX, offsetY);
    }

    private static void ProjectToOriginalFrame(
        IEnumerable<YoloBoundingBox> boxes,
        float scale,
        int offsetX,
        int offsetY,
        int originalWidth,
        int originalHeight)
    {
        if (boxes == null)
        {
            return;
        }

        foreach (var box in boxes)
        {
            var x = (box.Dimensions.X - offsetX) / scale;
            var y = (box.Dimensions.Y - offsetY) / scale;
            var width = box.Dimensions.Width / scale;
            var height = box.Dimensions.Height / scale;

            box.Dimensions.X = Math.Clamp(x, 0, Math.Max(0, originalWidth - 1));
            box.Dimensions.Y = Math.Clamp(y, 0, Math.Max(0, originalHeight - 1));
            box.Dimensions.Width = Math.Clamp(width, 0, originalWidth - box.Dimensions.X);
            box.Dimensions.Height = Math.Clamp(height, 0, originalHeight - box.Dimensions.Y);
        }
    }

    private bool IsChannelFirst(Tensor<float> tensor)
    {
        if (tensor.Rank < 4)
        {
            return true;
        }

        var dims = tensor.Dimensions.ToArray();

        // ONNX outputs are typically either [1, C, H, W] or [1, H, W, C].
        // Prefer the ordering that aligns the channel count with the expected parser layout.
        int channelIndex = Array.IndexOf(dims, _channelCount);

        if (channelIndex == 1)
        {
            return true; // NCHW
        }

        if (channelIndex == dims.Length - 1)
        {
            return false; // NHWC
        }

        // Fallback to channel-first when the layout is ambiguous.
        var heightIndex = Array.IndexOf(dims, _inputHeight);
        var widthIndex = Array.IndexOf(dims, _inputWidth);

        // If dimensions match NHWC (1, H, W, C) prefer that ordering; otherwise default to NCHW
        if (heightIndex == 1 && widthIndex == 2 && dims.Last() == _channelCount)
        {
            return false;
        }

        // Default: channel-first (1, C, H, W)
        return true;
    }

    private DenseTensor<float> ExtractTensor(Bitmap bitmap)
    {
        int batch = 1;
        if (_inputChannelFirst)
        {
            var tensor = new DenseTensor<float>(new[] { batch, 3, _inputHeight, _inputWidth });
            CopyBitmapToTensor(bitmap, tensor, channelFirst: true);
            return tensor;
        }
        else
        {
            var tensor = new DenseTensor<float>(new[] { batch, _inputHeight, _inputWidth, 3 });
            CopyBitmapToTensor(bitmap, tensor, channelFirst: false);
            return tensor;
        }
    }

    private void CopyBitmapToTensor(Bitmap bitmap, DenseTensor<float> tensor, bool channelFirst)
    {
        var rect = new Rectangle(0, 0, bitmap.Width, bitmap.Height);
        var bitmapData = bitmap.LockBits(rect, ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);

        try
        {
            int bytes = bitmapData.Stride * bitmapData.Height;
            var buffer = new byte[bytes];
            Marshal.Copy(bitmapData.Scan0, buffer, 0, bytes);

            for (int y = 0; y < bitmapData.Height; y++)
            {
                int rowOffset = y * bitmapData.Stride;
                for (int x = 0; x < bitmapData.Width; x++)
                {
                    int pixelOffset = rowOffset + x * 3;
                    float b = buffer[pixelOffset] / 255f;
                    float g = buffer[pixelOffset + 1] / 255f;
                    float r = buffer[pixelOffset + 2] / 255f;

                    if (channelFirst)
                    {
                        tensor[0, 0, y, x] = r;
                        tensor[0, 1, y, x] = g;
                        tensor[0, 2, y, x] = b;
                    }
                    else
                    {
                        tensor[0, y, x, 0] = r;
                        tensor[0, y, x, 1] = g;
                        tensor[0, y, x, 2] = b;
                    }
                }
            }
        }
        finally
        {
            bitmap.UnlockBits(bitmapData);
        }
    }

    private static bool DetermineChannelFirst(int[] dimensions)
    {
        if (dimensions.Length < 4)
        {
            return true;
        }

        // Prefer explicit positions when available, otherwise fall back to default NCHW.
        int channelIndex = Array.IndexOf(dimensions, 3);
        if (channelIndex == 1)
        {
            return true;
        }

        if (channelIndex == dimensions.Length - 1)
        {
            return false;
        }

        return true;
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _session.Dispose();
        _disposed = true;
        GC.SuppressFinalize(this);
    }
}
