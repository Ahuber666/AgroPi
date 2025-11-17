using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using ObjectDetectionCamera.Config;

namespace ObjectDetectionCamera.Yolo;

public class YoloOutputParser
{
    private const int ROW_COUNT = 13;
    private const int COL_COUNT = 13;
    private const int BOXES_PER_CELL = 5;
    private const int BOX_INFO_FEATURE_COUNT = 5;
    private const int CELL_WIDTH = AppConfig.InputWidth / COL_COUNT;
    private const int CELL_HEIGHT = AppConfig.InputHeight / ROW_COUNT;

    private readonly float[] _anchors = { 1.08f, 1.19f, 3.42f, 4.41f, 6.63f, 11.38f, 9.42f, 5.11f, 16.62f, 10.52f };
    private readonly string[] _labels;
    private readonly Color[] _colors;
    private readonly int _classCount;
    private readonly int _channelCount;

    public YoloOutputParser(string labelsPath)
    {
        if (!File.Exists(labelsPath))
        {
            throw new FileNotFoundException($"Labels file not found at {labelsPath}", labelsPath);
        }

        _labels = File.ReadAllLines(labelsPath)
            .Where(line => !string.IsNullOrWhiteSpace(line))
            .Select(line => line.Trim())
            .ToArray();

        if (_labels.Length == 0)
        {
            throw new InvalidOperationException("Labels file does not contain any entries.");
        }

        _classCount = _labels.Length;
        _channelCount = BOXES_PER_CELL * (_classCount + BOX_INFO_FEATURE_COUNT);
        _colors = GenerateColors(_labels.Length);
    }

    public IList<YoloBoundingBox> ParseOutputs(
        float[] modelOutput,
        float scoreThreshold,
        float iouThreshold,
        int imageWidth,
        int imageHeight)
    {
        if (modelOutput == null)
        {
            throw new ArgumentNullException(nameof(modelOutput));
        }

        var expectedLength = _channelCount * ROW_COUNT * COL_COUNT;

        if (modelOutput.Length != expectedLength)
        {
            throw new ArgumentException($"Unexpected model output length {modelOutput.Length}. Expected {expectedLength}.", nameof(modelOutput));
        }

        var boxes = ExtractBoundingBoxes(modelOutput, scoreThreshold);
        var ordered = boxes.OrderByDescending(b => b.Confidence).ToList();
        var results = new List<YoloBoundingBox>();

        while (ordered.Count > 0)
        {
            var candidate = ordered[0];
            ordered.RemoveAt(0);
            results.Add(candidate);

            for (int i = ordered.Count - 1; i >= 0; i--)
            {
                if (ordered[i].Label == candidate.Label &&
                    IntersectionOverUnion(candidate.Rect, ordered[i].Rect) >= iouThreshold)
                {
                    ordered.RemoveAt(i);
                }
            }
        }

        var xScale = imageWidth / (float)AppConfig.InputWidth;
        var yScale = imageHeight / (float)AppConfig.InputHeight;

        foreach (var box in results)
        {
            box.Dimensions.X = Math.Clamp(box.Dimensions.X * xScale, 0, Math.Max(0, imageWidth - 1));
            box.Dimensions.Y = Math.Clamp(box.Dimensions.Y * yScale, 0, Math.Max(0, imageHeight - 1));
            box.Dimensions.Width = Math.Clamp(box.Dimensions.Width * xScale, 0, imageWidth - box.Dimensions.X);
            box.Dimensions.Height = Math.Clamp(box.Dimensions.Height * yScale, 0, imageHeight - box.Dimensions.Y);
        }

        return results;
    }

    private List<YoloBoundingBox> ExtractBoundingBoxes(float[] modelOutput, float scoreThreshold)
    {
        var boxes = new List<YoloBoundingBox>();

        for (int row = 0; row < ROW_COUNT; row++)
        {
            for (int col = 0; col < COL_COUNT; col++)
            {
                for (int box = 0; box < BOXES_PER_CELL; box++)
                {
                    int channel = box * (_classCount + BOX_INFO_FEATURE_COUNT);
                    float x = (col + Sigmoid(modelOutput[GetOffset(channel, col, row)])) * CELL_WIDTH;
                    float y = (row + Sigmoid(modelOutput[GetOffset(channel + 1, col, row)])) * CELL_HEIGHT;
                    float width = MathF.Exp(modelOutput[GetOffset(channel + 2, col, row)]) * _anchors[box * 2] * CELL_WIDTH;
                    float height = MathF.Exp(modelOutput[GetOffset(channel + 3, col, row)]) * _anchors[box * 2 + 1] * CELL_HEIGHT;
                    float objectness = Sigmoid(modelOutput[GetOffset(channel + 4, col, row)]);

                    var classProbabilities = ExtractClasses(modelOutput, channel, col, row);
                    var (classIndex, classScore) = GetTopResult(classProbabilities);
                    float confidence = GetConfidence(objectness, classScore);

                    if (confidence < scoreThreshold)
                    {
                        continue;
                    }

                    var dimensions = MapBoundingBoxToCell(x, y, width, height);
                    int labelIndex = Math.Clamp(classIndex, 0, _labels.Length - 1);

                    boxes.Add(new YoloBoundingBox
                    {
                        Dimensions = dimensions,
                        Confidence = confidence,
                        Label = _labels[labelIndex],
                        BoxColor = _colors[labelIndex]
                    });
                }
            }
        }

        return boxes;
    }

    private static float Sigmoid(float value) => 1f / (1f + MathF.Exp(-value));

    private static float[] Softmax(float[] values)
    {
        var result = new float[values.Length];
        var max = values.Max();
        float sum = 0f;

        for (int i = 0; i < values.Length; i++)
        {
            result[i] = MathF.Exp(values[i] - max);
            sum += result[i];
        }

        if (sum == 0)
        {
            return result;
        }

        for (int i = 0; i < result.Length; i++)
        {
            result[i] /= sum;
        }

        return result;
    }

    private static int GetOffset(int channel, int x, int y)
    {
        return channel * ROW_COUNT * COL_COUNT + y * COL_COUNT + x;
    }

    private float[] ExtractClasses(float[] modelOutput, int channel, int x, int y)
    {
        var classes = new float[_classCount];
        for (int i = 0; i < _classCount; i++)
        {
            classes[i] = modelOutput[GetOffset(channel + BOX_INFO_FEATURE_COUNT + i, x, y)];
        }

        return Softmax(classes);
    }

    private static (int index, float score) GetTopResult(float[] classProbabilities)
    {
        int maxIndex = 0;
        float max = classProbabilities[0];

        for (int i = 1; i < classProbabilities.Length; i++)
        {
            if (classProbabilities[i] > max)
            {
                max = classProbabilities[i];
                maxIndex = i;
            }
        }

        return (maxIndex, max);
    }

    private static float GetConfidence(float objectness, float classProbability) => objectness * classProbability;

    private static BoundingBoxDimensions MapBoundingBoxToCell(float x, float y, float width, float height)
    {
        return new BoundingBoxDimensions
        {
            X = Math.Max(0, x - width / 2f),
            Y = Math.Max(0, y - height / 2f),
            Width = width,
            Height = height
        };
    }

    private static float IntersectionOverUnion(RectangleF boundingBoxA, RectangleF boundingBoxB)
    {
        float areaA = boundingBoxA.Width * boundingBoxA.Height;
        float areaB = boundingBoxB.Width * boundingBoxB.Height;

        if (areaA <= 0 || areaB <= 0)
        {
            return 0;
        }

        float minX = Math.Max(boundingBoxA.Left, boundingBoxB.Left);
        float minY = Math.Max(boundingBoxA.Top, boundingBoxB.Top);
        float maxX = Math.Min(boundingBoxA.Right, boundingBoxB.Right);
        float maxY = Math.Min(boundingBoxA.Bottom, boundingBoxB.Bottom);

        float intersectionArea = Math.Max(maxX - minX, 0) * Math.Max(maxY - minY, 0);

        return intersectionArea / (areaA + areaB - intersectionArea);
    }

    private static Color[] GenerateColors(int count)
    {
        Color[] palette =
        {
            Color.Red,
            Color.Blue,
            Color.Lime,
            Color.Orange,
            Color.Purple,
            Color.Cyan,
            Color.Magenta,
            Color.YellowGreen,
            Color.DeepPink,
            Color.Gold
        };

        var colors = new Color[count];
        for (int i = 0; i < count; i++)
        {
            colors[i] = palette[i % palette.Length];
        }

        return colors;
    }
}
