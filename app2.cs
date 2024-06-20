using System;
using System.IO;
using SkiaSharp;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;
using UglyToad.PdfPig;
using UglyToad.PdfPig.Content;

namespace PdfToBlackWhitePng
{
    class Program
    {
        static void Main(string[] args)
        {
            string pdfPath = "path/to/your/input.pdf";
            string outputPath = "path/to/your/output.png";

            ConvertPdfToBlackWhitePng(pdfPath, outputPath);
        }

        static void ConvertPdfToBlackWhitePng(string pdfPath, string outputPath)
        {
            using (PdfDocument document = PdfDocument.Open(pdfPath))
            {
                Page page = document.GetPage(1);

                int dpi = 300; // Adjust DPI as needed
                int width = (int)(page.Width * dpi / 72.0);
                int height = (int)(page.Height * dpi / 72.0);

                using (SKBitmap bitmap = new SKBitmap(width, height))
                using (SKCanvas canvas = new SKCanvas(bitmap))
                {
                    canvas.Clear(SKColors.White);

                    // Render the PDF content onto the canvas
                    DrawPageContent(page, canvas, dpi);

                    using (var image = SKImage.FromBitmap(bitmap))
                    using (var data = image.Encode(SKEncodedImageFormat.Png, 100))
                    using (var memoryStream = new MemoryStream())
                    {
                        data.SaveTo(memoryStream);
                        memoryStream.Seek(0, SeekOrigin.Begin);

                        using (var imageSharp = SixLabors.ImageSharp.Image.Load<Rgba32>(memoryStream))
                        {
                            // Convert to 1-bit black and white
                            imageSharp.Mutate(x => x.BinaryThreshold(0.5f));

                            // Save the output image
                            imageSharp.Save(outputPath);
                        }
                    }
                }
            }
        }

        static void DrawPageContent(Page page, SKCanvas canvas, int dpi)
        {
            // Render text
            foreach (var letter in page.Letters)
            {
                var paint = new SKPaint
                {
                    Color = SKColors.Black,
                    TextSize = letter.FontSize * dpi / 72.0f
                };
                canvas.DrawText(letter.Value, letter.GlyphRectangle.Left * dpi / 72.0f, (page.Height - letter.GlyphRectangle.Top) * dpi / 72.0f, paint);
            }

            // Render images
            foreach (var image in page.GetImages())
            {
                using (var skImage = SKImage.FromEncodedData(image.RawBytes))
                using (var skBitmap = SKBitmap.FromImage(skImage))
                {
                    var srcRect = new SKRect(0, 0, skBitmap.Width, skBitmap.Height);
                    var destRect = new SKRect(
                        image.Bounds.Left * dpi / 72.0f,
                        (page.Height - image.Bounds.Bottom) * dpi / 72.0f,
                        image.Bounds.Right * dpi / 72.0f,
                        (page.Height - image.Bounds.Top) * dpi / 72.0f
                    );

                    canvas.DrawBitmap(skBitmap, srcRect, destRect);
                }
            }
        }
    }
}
