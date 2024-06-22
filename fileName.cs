using System;
using System.IO;
using SkiaSharp;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;
using UglyToad.PdfPig;
using UglyToad.PdfPig.Content;
using System.Diagnostics;
using System.Reflection.Metadata;
using System.Drawing;

string pdfPath = "D:\\MyProgram\\CSharp\\PDFtoImage\\input.pdf";
string outputPath = "D:\\MyProgram\\CSharp\\PDFtoImage\\output.png";
string imagePath= "D:\\MyProgram\\CSharp\\PDFtoImage\\bg_output.png";

ConvertPdfToBlackWhitePng(pdfPath, outputPath);


void ConvertPdfToBlackWhitePng(string pdfPath, string outputPath)
{
    using (PdfDocument document = PdfDocument.Open(pdfPath))
    {
        Console.WriteLine(document.GetPages().Count());

        Page page = document.GetPage(1);



        int dpi = 300; // High resolution
        int width = (int)(page.Width * dpi / 72.0);
        int height = (int)(page.Height * dpi / 72.0);




        using (var inputStream = File.OpenRead(imagePath))
        using (var bitmap = SKBitmap.Decode(inputStream))
        using (var canvas = new SKCanvas(bitmap))
        {
            /*canvas.Clear(SKColors.White);*/

            // Render the PDF content onto the canvas
            DrawPageContent(page, canvas, dpi);

            using (var image = SKImage.FromBitmap(bitmap))
            using (var data = image.Encode(SKEncodedImageFormat.Png, 100))
            using (var memoryStream = new MemoryStream())
            {
                data.SaveTo(memoryStream);
                memoryStream.Seek(0, SeekOrigin.Begin);

                /*using (var imageSharp = SixLabors.ImageSharp.Image.Load<Rgba32>(memoryStream))*/
                using (var imageSharp = SixLabors.ImageSharp.Image.Load<Rgba1010102>(memoryStream))
                {
                    // Convert to black and white 1-bit
                    imageSharp.Mutate(x => x.BinaryThreshold(0.5f).Grayscale());


                    var quantizer = new SixLabors.ImageSharp.Processing.Processors.Quantization.WebSafePaletteQuantizer();
                    using (Image<L8> grayscaleImage = imageSharp.CloneAs<L8>())
                    {
                        grayscaleImage.Mutate(ctx => ctx.Quantize(quantizer));

                        // Save the modified image as a new 8-bit PNG file
                        grayscaleImage.Save(outputPath);
                    }


                    // Save the output image
                    /*imageSharp.Save(outputPath);*/
                }
            }
        }
    }

}



void DrawPageContent(Page page, SKCanvas canvas, int dpi)
{


    foreach (var letter in page.Letters)
    {
        float fontDPI = dpi / 72.0f;

        var rectPaint = new SKPaint
        {
            Color = SKColors.Blue
        };

        var rect = new SKRect((float)letter.Location.X* fontDPI, (float)(page.Height - letter.Location.Y) * fontDPI, (float)(letter.Location.X* fontDPI+letter.Width), (float)((page.Height - letter.Location.Y) * fontDPI+letter.Width));
        canvas.DrawRect(rect, rectPaint);




        /*   letter.Location.*/
        var typeface = SKTypeface.FromFamilyName("Tahoma", SKFontStyleWeight.Bold, SKFontStyleWidth.Normal, SKFontStyleSlant.Upright);



        var paint = new SKPaint
        {
            Color = SKColors.Black,
            Typeface = typeface,
            TextSize = (float)(letter.FontSize * fontDPI)
        };


        /* canvas.DrawText(letter.Value, (float)letter.GlyphRectangle.Left * dpi / 72.0f, (float)(page.Height - letter.GlyphRectangle.Top) * dpi / 72.0f, paint);  */




        canvas.DrawText(letter.Value, (float)letter.Location.X* fontDPI, (float)(page.Height - letter.Location.Y) * fontDPI, paint);





    }

    Console.WriteLine(page.Text);
    Console.WriteLine("page.GetImages().Count()");
    Console.WriteLine(page.GetImages().Count());

    Console.WriteLine("page.GetMarkedContents().Count()");
    Console.WriteLine(page.GetMarkedContents().Count());


    foreach (var image in page.GetImages())
    {
        // Render images if any. Custom logic might be required depending on the QR code rendering.


        using (var skImage = SKImage.FromEncodedData(new MemoryStream((byte[])image.RawBytes)))
        using (var skBitmapColor = SKBitmap.FromImage(skImage))
        using (var skBitmap = new SKBitmap(skBitmapColor.Width, skBitmapColor.Height, SKColorType.Gray8, SKAlphaType.Opaque))
        {
            var srcRect = new SKRect(0, 0, skBitmap.Width, skBitmap.Height);
            var destRect = new SKRect(
                (float)image.Bounds.Left * dpi / 72.0f,
                (float)(page.Height - image.Bounds.Bottom) * dpi / 72.0f,
                (float)image.Bounds.Right * dpi / 72.0f,
                (float)(page.Height - image.Bounds.Top) * dpi / 72.0f
            );

            canvas.DrawBitmap(skBitmap, srcRect, destRect);
        }
    }


    var markedContents = page.GetMarkedContents();

    foreach (var markedContent in markedContents)
    {
        if (markedContent != null)
        {
            Console.WriteLine($"Marked content on page {page.Number}:");
            markedContent.Images.Count();


            /*PrintMarkedContent(markedContent);*/
        }
    }



    // Add additional rendering logic as needed for other PDF content (lines, shapes, etc.)
}

static SKBitmap ConvertTo8BitGrayscale(SKBitmap bitmap)
{
    var grayscaleBitmap = new SKBitmap(bitmap.Width, bitmap.Height, SKColorType.Gray8, SKAlphaType.Opaque);
    using (var canvas = new SKCanvas(grayscaleBitmap))
    {
        var paint = new SKPaint
        {
            ColorFilter = SKColorFilter.CreateColorMatrix(new float[]
            {
                    0.3f, 0.3f, 0.3f, 0, 0,
                    0.59f, 0.59f, 0.59f, 0, 0,
                    0.11f, 0.11f, 0.11f, 0, 0,
                    0, 0, 0, 1, 0
            })
        };
        canvas.DrawBitmap(bitmap, 0, 0, paint);
    }
    return grayscaleBitmap;
}
