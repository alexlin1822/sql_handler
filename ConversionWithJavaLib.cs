using System;
using System.IO;
using SkiaSharp;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;
using UglyToad.PdfPig;
using UglyToad.PdfPig.Content;
using System.Diagnostics;
using System.Drawing;

namespace PdfToBlackWhitePng
{
    class ConversionWithJavaLib
    {
        static string current_path = Directory.GetCurrentDirectory();

        /**
         * Convert PDF to B/W PNG image with custom parameter
         * @param pdfFilePathAndName  	Input PDF file path and name
         * @param outputPathLandscape	Path for Output PNG files (Landscape)
         * @param outputPathPortrait	Path for Output PNG files (Portrait)
         * @param tempImagePath       	Path for temporary PNG files (QR CODE image)
         * @param dpi_str				Output DPI
         * @param threshold_str			Control document darker or lighter. Adjust the threshold between 0 to 255. 0 is lighter. 255 is darker.
         */
        public static void ConvertPdfToBlackWhitePng(string pdfFilePathAndName, string outputPathLandscape, string outputPathPortrait, string tempImagePath, string dpi_str, string threshold_str)
        {

            string fileName = Path.GetFileNameWithoutExtension(pdfFilePathAndName);

            int dpi = Int32.Parse(dpi_str);
            int threshold = Int32.Parse(threshold_str);

            using (UglyToad.PdfPig.PdfDocument document = UglyToad.PdfPig.PdfDocument.Open(pdfFilePathAndName))
            {
                for (int i = 0; i < document.GetPages().Count(); i++)
                {

                    string tempImageFile = tempImagePath + "\\" + fileName + "_" + i.ToString() + "_tmp.png";
                    string outputFile_Landscape = outputPathLandscape + "\\" + fileName + "_" + (i + 1).ToString() + "_Landscape.png";
                    string outputFile_Portrait = outputPathPortrait + "\\" + fileName + "_" + (i + 1).ToString() + "_Portrait.png";

                    Console.WriteLine("Input PDF file : " + pdfFilePathAndName);

                    //Create png image
                    ConvertQRCode(pdfFilePathAndName, tempImageFile, i.ToString(), dpi_str, threshold_str);

                    //replace the text
                    Page page = document.GetPage(i + 1);

                    int width = (int)(page.Width * dpi / 72.0);
                    int height = (int)(page.Height * dpi / 72.0);

                    //use a image as background
                    using (var inputStream = File.OpenRead(tempImageFile))
                    using (var bitmap = SKBitmap.Decode(inputStream))
                    using (SKCanvas canvas = new SKCanvas(bitmap))
                    {
                        //canvas.Clear(SKColors.White);

                        // Render the PDF content onto the canvas
                        DrawPageContent(page, canvas, dpi);

                        using (var image = SKImage.FromBitmap(bitmap))
                        using (var data = image.Encode(SKEncodedImageFormat.Png, 100))
                        using (var memoryStream = new MemoryStream())
                        {
                            data.SaveTo(memoryStream);
                            memoryStream.Seek(0, SeekOrigin.Begin);

                            using (var imageSharp = SixLabors.ImageSharp.Image.Load<Rgba32>(memoryStream))
                            // using (var imageSharp = SixLabors.ImageSharp.Image.Load<Rgba1010102>(memoryStream))
                            {
                                // Convert to 1-bit black and white
                                imageSharp.Mutate(x => x.BinaryThreshold(0.5f));

                                // Save the output image
                                imageSharp.Save(outputFile_Landscape);
                            }
                        }
                    }

                    using (var originalBitmap = SKBitmap.Decode(outputFile_Landscape))
                    {
                        // Convert to 8-bit and save the original PNG
                        using (var skBitmap8bpp = ConvertTo8bpp(originalBitmap))
                        {
                            // SaveBitmap(skBitmap8bpp, outputFilePathOriginal);

                            // Rotate the PNG by 90 degrees and save
                            using (var rotatedBitmap8bpp = RotateCanvas(skBitmap8bpp, 90))
                            {
                                SaveBitmap(rotatedBitmap8bpp, outputFile_Portrait);
                            }
                        }

                        Console.WriteLine("Images saved successfully.");
                    }
                    // Console.WriteLine(page.Text);
                    Console.WriteLine("PNG file conversion completed!");
                    Console.WriteLine("Output PNG file : " + outputFile_Landscape);
                    Console.WriteLine("Output PNG file : " + outputFile_Portrait);
                    Console.WriteLine("-------------------------------------------");

                    // Delete temp file
                    if (File.Exists(tempImageFile))
                    {
                        File.Delete(tempImageFile);
                    }
                }
            }
        }

        /**
         * Convert PDF to B/W PNG image with custom parameter
         * @param pdfFilePathAndName  		Input PDF file path and name
         * @param outputPathLandscape	Path for Output PNG files (Landscape)
         * @param outputPathPortrait	Path for Output PNG files (Portrait)
         * @param tempImagePath       	Path for temporary PNG files (QR CODE image)
         * @param dpi_str				Output DPI
         * @param threshold_str			Control document darker or lighter. Adjust the threshold between 0 to 255. 0 is lighter. 255 is darker.
         */
        private static bool ConvertQRCode(string pdfFilePathAndName, string imageBG, string pageNumber, string dpi, string threshold)
        {

            Stopwatch stopwatchQR = new Stopwatch();
            stopwatchQR.Start();

            // Path to the Java executable
            string javaPath = "java";

            // Path to the JAR file
            string jarPath = current_path + "\\pdf2png.jar";

            // Create the process start info
            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.FileName = javaPath;
            startInfo.Arguments = $"-jar \"{jarPath}\" \"{pdfFilePathAndName}\" \"{imageBG}\" \"{pageNumber}\" \"{dpi}\" \"{threshold}\"";
            startInfo.UseShellExecute = false;
            startInfo.RedirectStandardOutput = true;
            startInfo.RedirectStandardError = true;

            try
            {
                // Start the process
                using (Process process = new Process())
                {
                    process.StartInfo = startInfo;
                    process.Start();

                    // Read the output (or error)
                    string output = process.StandardOutput.ReadToEnd();
                    string error = process.StandardError.ReadToEnd();

                    process.WaitForExit();

                    // Display the output
                    Console.WriteLine("Output:");
                    Console.WriteLine(output);

                    // Display the error (if any)
                    if (!string.IsNullOrEmpty(error))
                    {
                        Console.WriteLine("Error:");
                        Console.WriteLine(error);
                    }
                }
                stopwatchQR.Stop();
                Console.WriteLine("ConvertQRCode Spent time: " + stopwatchQR.ElapsedMilliseconds + " ms");

                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine("An error occurred while trying to run the Java application.");
                Console.WriteLine(ex.Message);

                stopwatchQR.Stop();
                Console.WriteLine("ConvertQRCode Spent time: " + stopwatchQR.ElapsedMilliseconds + " ms");
                return false;
            }


        }

        /**
         * Convert 24 bit image to 8 bit image
         * @param bitmap  		24 bit image
         * @return              8 bit image
         */
        private static SKBitmap ConvertTo8bpp(SKBitmap bitmap)
        {
            int width = bitmap.Width;
            int height = bitmap.Height;

            // Create a new SKBitmap with Gray8 color type
            SKBitmap skBitmap8bpp = new SKBitmap(width, height, SKColorType.Gray8, SKAlphaType.Opaque);

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    SKColor color = bitmap.GetPixel(x, y);
                    byte grayValue = (byte)((color.Red + color.Green + color.Blue) / 3);
                    skBitmap8bpp.SetPixel(x, y, new SKColor(grayValue, grayValue, grayValue));
                }
            }

            return skBitmap8bpp;
        }

        /**
         * Rotate image with a specific degree 
         * @param bitmap  		original image
         * degrees              rotate image with a specific degree 
         * @return              rotated image
         */
        private static SKBitmap RotateCanvas(SKBitmap bitmap, float degrees)
        {
            int width = bitmap.Width;
            int height = bitmap.Height;

            // Create a new SKBitmap with swapped dimensions
            SKBitmap rotatedBitmap = new SKBitmap(height, width, SKColorType.Gray8, SKAlphaType.Opaque);

            using (var canvas = new SKCanvas(rotatedBitmap))
            {
                // Move the canvas origin to the center of the new bitmap
                canvas.Translate(height / 2, width / 2);
                canvas.RotateDegrees(degrees);
                canvas.Translate(-width / 2, -height / 2);

                // Draw the original bitmap onto the rotated canvas
                canvas.DrawBitmap(bitmap, 0, 0);
            }

            return rotatedBitmap;
        }


        /**
         * Save image to png image 
         * @param bitmap  		original image
         * filePath             filePath
         */
        private static void SaveBitmap(SKBitmap bitmap, string filePath)
        {
            using (SKImage image = SKImage.FromBitmap(bitmap))
            using (SKData data = image.Encode(SKEncodedImageFormat.Png, 100))
            using (var stream = File.OpenWrite(filePath))
            {
                data.SaveTo(stream);
            }
        }

        /**
         * Draw Page Text Content
         * @param page  		pdf page
         * @param canvas        SKCanvas canvas for writing the text 
         * @dpi                 image dpi
         */
        private static void DrawPageContent(Page page, SKCanvas canvas, int dpi)
        {

            float final_dpi = dpi / 72.0f;

            // Render text
            foreach (var letter in page.Letters)
            {
                // Get the font
                string fontnameString = letter.FontName;
                string[] parts = fontnameString.Split('+');
                string fontname = "Tahoma";

                fontname = parts.Length > 1 ? parts[1] : parts[0];

                string[] fontParts = fontname.Split(',');

                bool isBold = false;
                if (fontParts.Length > 1)
                {
                    fontname = fontParts[0];
                    if (fontParts[1] == "Bold")
                    {
                        isBold = true;
                    }
                }

                /* Write the text white background on canvas */
                var rectPaint = new SKPaint
                {
                    Color = SKColors.White
                };

                double fontHeight = letter.GlyphRectangle.Top - letter.GlyphRectangle.Bottom + 0.2;
                if (fontHeight < 3.0)
                {
                    fontHeight = 4.8;
                }
                var rect = new SKRect((float)letter.Location.X * final_dpi, (float)((page.Height - letter.Location.Y - fontHeight) * final_dpi), (float)((letter.Location.X + letter.Width) * final_dpi), (float)((page.Height - letter.Location.Y + 1.5) * final_dpi));
                if (letter.FontSize > 2.0)
                {
                    canvas.DrawRect(rect, rectPaint);
                }

                /* Write the text on canvas */
                float letterSize = (float)letter.FontSize * final_dpi;

                string letStr = letter.Value;

                var typeface = SKTypeface.FromFamilyName(fontname, isBold ? SKFontStyleWeight.Bold : SKFontStyleWeight.Normal, SKFontStyleWidth.Normal, SKFontStyleSlant.Upright);
                // var typeface = SKTypeface.FromFamilyName(fontname, isBold ? SKFontStyleWeight.Thin : SKFontStyleWeight.Thin, 1, SKFontStyleSlant.Upright);

                var paint = new SKPaint
                {
                    Color = SKColors.Black,
                    Typeface = typeface,
                    TextSize = letterSize,
                    TextAlign = SKTextAlign.Left,
                    TextScaleX = 1

                };

                if (letter.FontSize > 2.0)
                {
                    canvas.DrawText(letStr, (float)letter.Location.X * final_dpi, (float)(page.Height - letter.Location.Y) * final_dpi, paint);
                }

                // Console.WriteLine(letter.FontName + " -> " + fontname + " = " + letter.Value + " " + letter.FontSize + " Left=" + letter.Location.X + "   top= " + letter.Location.Y + "   bottom= " + letter.GlyphRectangle.Bottom + "   Height= " + (letter.GlyphRectangle.Bottom - letter.GlyphRectangle.Top));
            }

            // Render images
            foreach (var image in page.GetImages())
            {
                using (var skImage = SKImage.FromEncodedData(new MemoryStream((byte[])image.RawBytes)))
                using (var skBitmap = SKBitmap.FromImage(skImage))
                {
                    Console.WriteLine("image");
                    var srcRect = new SKRect(0, 0, skBitmap.Width, skBitmap.Height);
                    var destRect = new SKRect(
                        (float)image.Bounds.Left * final_dpi,
                        (float)(page.Height - image.Bounds.Bottom) * final_dpi,
                        (float)image.Bounds.Right * final_dpi,
                        (float)(page.Height - image.Bounds.Top) * final_dpi
                    );

                    canvas.DrawBitmap(skBitmap, srcRect, destRect);
                }
            }
        }
    }
}
