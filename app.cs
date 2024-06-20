using System;
using System.IO;
using SkiaSharp;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;
using UglyToad.PdfPig;
using UglyToad.PdfPig.Content;
using System.Diagnostics;

string pdfPath = "D:\\MyProgram\\CSharp\\PDFtoImage\\input.pdf";
string outputPath = "D:\\MyProgram\\CSharp\\PDFtoImage\\output.png";

ConvertPdfToBlackWhitePng(pdfPath, outputPath);

void ConvertPdfToBlackWhitePng(string pdfPath, string outputPath)
{
    using (PdfDocument document = PdfDocument.Open(pdfPath))
    {
        Page page = document.GetPage(1);

        int dpi = 600; // High resolution
        int width = (int)(page.Width * dpi / 72.0);
        int height = (int)(page.Height * dpi / 72.0);

        using (SKBitmap bitmap = new SKBitmap(width, height))
        using (SKCanvas canvas = new SKCanvas(bitmap))
        {
            canvas.Clear(SKColors.White);

            // Render the PDF content onto the canvas
            DrawPageContent(page, canvas, dpi);

            using (var image = SKImage.FromBitmap(bitmap))
            /*using (var image = SKImage.FromBitmap(bitmap))*/
            using (var data = image.Encode(SKEncodedImageFormat.Png, 100))
            using (var memoryStream = new MemoryStream())
            {
                data.SaveTo(memoryStream);
                memoryStream.Seek(0, SeekOrigin.Begin);

                using (var imageSharp = SixLabors.ImageSharp.Image.Load<Rgba32>(memoryStream))
                {
                    // Convert to black and white 1-bit
                    imageSharp.Mutate(x => x.BinaryThreshold(0.5f).Grayscale());

                    // Save the output image
                    imageSharp.Save(outputPath);
                }
            }
            

        }
    }
}


static SKBitmap ConvertTo1Bit(SKBitmap inputBitmap)
{
    // Create a new SKBitmap with 1-bit per pixel
    SKBitmap outputBitmap = new SKBitmap(inputBitmap.Width, inputBitmap.Height, SKColorType.Gray8, SKAlphaType.Opaque);

    // Get the pixels of the input bitmap
    SKColor[] pixels = inputBitmap.Pixels;

    // Iterate through each pixel and convert to grayscale (1-bit)
    for (int i = 0; i < pixels.Length; i++)
    {
        // Convert pixel to grayscale
        byte grayscaleValue = (byte)(0.299 * pixels[i].Red + 0.587 * pixels[i].Green + 0.114 * pixels[i].Blue);

        // Set the pixel value in the output bitmap
        outputBitmap.Pixels[i] = grayscaleValue < 128 ? new SKColor(0, 0, 0) : new SKColor(255, 255, 255); // Threshold to black or white
    }

    return outputBitmap;
}

void DrawPageContent(Page page, SKCanvas canvas, int dpi)
{
    foreach (var letter in page.Letters)
    {

        var paint = new SKPaint
        {
            Color = SKColors.Black,
            TextSize = (float)(letter.FontSize * dpi / 72.0f*3)
        };
        canvas.DrawText(letter.Value, (float)letter.GlyphRectangle.Left * dpi / 72.0f, (float)(page.Height - letter.GlyphRectangle.Top) * dpi / 72.0f, paint);
    }

    foreach (var image in page.GetImages())
    {
        // Render images if any. Custom logic might be required depending on the QR code rendering.
    }

    // Add additional rendering logic as needed for other PDF content (lines, shapes, etc.)
}

