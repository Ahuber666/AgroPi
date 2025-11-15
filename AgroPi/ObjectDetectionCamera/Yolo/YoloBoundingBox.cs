using System.Drawing;

namespace ObjectDetectionCamera.Yolo;

public class BoundingBoxDimensions : DimensionsBase
{
}

public class YoloBoundingBox
{
    public BoundingBoxDimensions Dimensions { get; set; } = new();
    public string Label { get; set; } = string.Empty;
    public float Confidence { get; set; }
    public Color BoxColor { get; set; } = Color.Red;
    public RectangleF Rect => new(Dimensions.X, Dimensions.Y, Dimensions.Width, Dimensions.Height);
}
