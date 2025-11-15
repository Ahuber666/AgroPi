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
    private bool _disposed;

    public OnnxYoloDetector(string modelPath, string labelsPath)
    {
        if (!File.Exists(modelPath))
        {
            throw new FileNotFoundException($"Unable to locate model at {modelPath}", modelPath);
        }

        _session = new InferenceSession(modelPath);
        _parser = new YoloOutputParser(labelsPath);
    }

    public IList<YoloBoundingBox> Detect(Bitmap bitmap)
    {
        if (bitmap == null)
        {
            throw new ArgumentNullException(nameof(bitmap));
        }

        using var resized = new Bitmap(AppConfig.InputWidth, AppConfig.InputHeight, PixelFormat.Format24bppRgb);
        using (var graphics = Graphics.FromImage(resized))
        {
            graphics.CompositingMode = System.Drawing.Drawing2D.CompositingMode.SourceCopy;
            graphics.CompositingQuality = System.Drawing.Drawing2D.CompositingQuality.HighSpeed;
            graphics.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.Bilinear;
            graphics.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighSpeed;
            graphics.DrawImage(bitmap, 0, 0, AppConfig.InputWidth, AppConfig.InputHeight);
        }

        var tensor = ExtractTensor(resized);

        var inputValue = DisposableNamedOnnxValue.CreateFromTensor(AppConfig.InputName, tensor);
        try
        {
            using IDisposableReadOnlyCollection<DisposableNamedOnnxValue> results = _session.Run(new[] { inputValue });
            var output = results.First(r => r.Name == AppConfig.OutputName).AsEnumerable<float>().ToArray();

            return _parser.ParseOutputs(output, AppConfig.ScoreThreshold, AppConfig.IoUThreshold, bitmap.Width, bitmap.Height);
        }
        finally
        {
            (inputValue as IDisposable)?.Dispose();
        }
    }

    private static DenseTensor<float> ExtractTensor(Bitmap bitmap)
    {
        var tensor = new DenseTensor<float>(new[] { 1, 3, AppConfig.InputHeight, AppConfig.InputWidth });
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

                    tensor[0, 0, y, x] = r;
                    tensor[0, 1, y, x] = g;
                    tensor[0, 2, y, x] = b;
                }
            }
        }
        finally
        {
            bitmap.UnlockBits(bitmapData);
        }

        return tensor;
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
