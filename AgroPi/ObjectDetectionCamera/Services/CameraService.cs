using System;
using System.Drawing;
using OpenCvSharp;
using OpenCvSharp.Extensions;

namespace ObjectDetectionCamera.Services;

public class CameraService : IDisposable
{
    private readonly object _sync = new();
    private VideoCapture? _capture;

    public bool Start(int cameraIndex = 0)
    {
        lock (_sync)
        {
            if (_capture != null && _capture.IsOpened())
            {
                return true;
            }

            _capture = new VideoCapture(cameraIndex);
            if (!_capture.IsOpened())
            {
                _capture.Dispose();
                _capture = null;
                return false;
            }

            _capture.Set(VideoCaptureProperties.FrameWidth, 1920);
            _capture.Set(VideoCaptureProperties.FrameHeight, 1080);
            _capture.Set(VideoCaptureProperties.Fps, 30);
            return true;
        }
    }

    public Bitmap? GrabFrame()
    {
        lock (_sync)
        {
            if (_capture == null || !_capture.IsOpened())
            {
                return null;
            }

            using var frame = new Mat();
            if (!_capture.Read(frame) || frame.Empty())
            {
                return null;
            }

            return BitmapConverter.ToBitmap(frame);
        }
    }

    public void Stop()
    {
        lock (_sync)
        {
            if (_capture == null)
            {
                return;
            }

            _capture.Release();
            _capture.Dispose();
            _capture = null;
        }
    }

    public void Dispose()
    {
        Stop();
        GC.SuppressFinalize(this);
    }
}
