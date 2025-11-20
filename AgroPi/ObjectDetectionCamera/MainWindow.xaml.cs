using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Interop;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Microsoft.Extensions.Logging;
using ObjectDetectionCamera.Config;
using ObjectDetectionCamera.Services;
using ObjectDetectionCamera.Yolo;

namespace ObjectDetectionCamera;

public partial class MainWindow : Window
{
    private readonly CameraService _camera = new();
    private readonly OnnxYoloDetector? _detector;
    private readonly ILoggerFactory? _loggerFactory;
    private readonly ILogger<MainWindow>? _logger;

    private CancellationTokenSource? _cts;
    private Task? _captureTask;
    private readonly bool _isReady;

    public MainWindow()
    {
        InitializeComponent();

        _loggerFactory = LoggerFactory.Create(builder => builder.AddSimpleConsole());
        _logger = _loggerFactory.CreateLogger<MainWindow>();

        if (!File.Exists(AppConfig.ModelPath) || !File.Exists(AppConfig.LabelsPath))
        {
            MessageBox.Show(
                "Missing model.onnx or labels.txt under the Model folder. Place the required files and restart the app.",
                "Missing assets",
                MessageBoxButton.OK,
                MessageBoxImage.Warning);
            StartButton.IsEnabled = false;
            return;
        }

        try
        {
            _detector = new OnnxYoloDetector(AppConfig.ModelPath, AppConfig.LabelsPath);
            _isReady = true;
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Failed to initialize the ONNX detector.");
            MessageBox.Show(
                $"Failed to initialize the ONNX model: {ex.Message}",
                "Initialization error",
                MessageBoxButton.OK,
                MessageBoxImage.Error);
            StartButton.IsEnabled = false;
        }
    }

    private void StartButton_Click(object sender, RoutedEventArgs e)
    {
        if (!_isReady || _detector == null || _cts != null)
        {
            return;
        }

        _cts = new CancellationTokenSource();

        if (!_camera.Start())
        {
            _logger?.LogWarning("Unable to open the webcam.");
            MessageBox.Show(
                "Unable to start the camera. Ensure the Logitech BRIO is connected and not used by another application.",
                "Camera error",
                MessageBoxButton.OK,
                MessageBoxImage.Error);
            _cts.Dispose();
            _cts = null;
            return;
        }

        StartButton.IsEnabled = false;
        StopButton.IsEnabled = true;
        _captureTask = Task.Run(() => CaptureLoopAsync(_cts.Token));
    }

    private async void StopButton_Click(object sender, RoutedEventArgs e)
    {
        await StopCaptureAsync();
    }

    private async Task CaptureLoopAsync(CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            Bitmap? frame = null;

            try
            {
                frame = _camera.GrabFrame();
                if (frame == null)
                {
                    await Task.Delay(50, token);
                    continue;
                }

                IList<YoloBoundingBox> boxes = Array.Empty<YoloBoundingBox>();
                try
                {
                    boxes = _detector?.Detect(frame) ?? Array.Empty<YoloBoundingBox>();
                }
                catch (Exception ex)
                {
                    _logger?.LogError(ex, "Inference failed for the current frame.");
                }

                DrawDetections(frame, boxes);

                var bitmapSource = ConvertToBitmapSource(frame);
                await Dispatcher.InvokeAsync(
                    () => VideoImage.Source = bitmapSource,
                    DispatcherPriority.Render,
                    token);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Camera capture loop failure.");
                await Task.Delay(200, token);
            }
            finally
            {
                frame?.Dispose();
            }

            await Task.Delay(50, token);
        }
    }

    private async Task StopCaptureAsync()
    {
        var cts = Interlocked.Exchange(ref _cts, null);
        if (cts == null)
        {
            Dispatcher.Invoke(() =>
            {
                StartButton.IsEnabled = _isReady;
                StopButton.IsEnabled = false;
            });
            _camera.Stop();
            return;
        }

        cts.Cancel();

        try
        {
            if (_captureTask != null)
            {
                await _captureTask;
            }
        }
        catch (OperationCanceledException)
        {
            // expected during shutdown
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Error while stopping the capture loop.");
        }
        finally
        {
            cts.Dispose();
            _captureTask = null;
            _camera.Stop();
            Dispatcher.Invoke(() =>
            {
                StartButton.IsEnabled = _isReady;
                StopButton.IsEnabled = false;
            });
        }
    }

    protected override void OnClosing(CancelEventArgs e)
    {
        base.OnClosing(e);

        try
        {
            StopCaptureAsync().GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Error while closing the main window.");
        }
        finally
        {
            _camera.Dispose();
            _detector?.Dispose();
            _loggerFactory?.Dispose();
        }
    }

    private static void DrawDetections(Bitmap bitmap, IEnumerable<YoloBoundingBox> boxes)
    {
        using var graphics = Graphics.FromImage(bitmap);
        graphics.SmoothingMode = SmoothingMode.AntiAlias;
        using var font = new System.Drawing.Font("Segoe UI", 14, System.Drawing.FontStyle.Bold, GraphicsUnit.Pixel);

        foreach (var box in boxes ?? Array.Empty<YoloBoundingBox>())
        {
            var rect = box.Rect;
            using var pen = new System.Drawing.Pen(box.BoxColor, 3);
            graphics.DrawRectangle(pen, rect.X, rect.Y, rect.Width, rect.Height);

            var labelText = $"{box.Label} {box.Confidence:P0}";
            var textSize = graphics.MeasureString(labelText, font);
            var textRect = new System.Drawing.RectangleF(
                rect.X,
                Math.Max(0, rect.Y - textSize.Height),
                textSize.Width,
                textSize.Height);

            using var backgroundBrush = new System.Drawing.SolidBrush(Color.FromArgb(200, Color.Red));
            graphics.FillRectangle(backgroundBrush, textRect);
            graphics.DrawString(labelText, font, System.Drawing.Brushes.White, textRect.Location);
        }
    }

    private static BitmapSource ConvertToBitmapSource(Bitmap bitmap)
    {
        var handle = bitmap.GetHbitmap();
        try
        {
            var source = Imaging.CreateBitmapSourceFromHBitmap(
                handle,
                IntPtr.Zero,
                Int32Rect.Empty,
                BitmapSizeOptions.FromEmptyOptions());
            source.Freeze();
            return source;
        }
        finally
        {
            DeleteObject(handle);
        }
    }

    [DllImport("gdi32.dll")]
    private static extern bool DeleteObject(IntPtr hObject);
}
