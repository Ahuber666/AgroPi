using System;
using System.IO;

namespace ObjectDetectionCamera.Config;

public static class AppConfig
{
    public static string ModelPath => Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Model", "model.onnx");
    public static string LabelsPath => Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Model", "labels.txt");

    public const int InputWidth = 416;
    public const int InputHeight = 416;
    public const string InputName = "image";
    public const string OutputName = "grid";
    public const float ScoreThreshold = 0.3f;
    public const float IoUThreshold = 0.5f;
}
