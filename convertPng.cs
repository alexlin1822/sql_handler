using System;
using System.Drawing;
using System.Drawing.Imaging;

public class ImageConverter
{
      public static void Main()
    {
        string inputPath = "path/to/your/24bit/image.png";
        string output8BitPath = "path/to/save/8bit/image.png";
        string output1BitPath = "path/to/save/1bit/image.png";
        
        ImageConverter.ConvertTo8Bit(inputPath, output8BitPath);
        ImageConverter.ConvertTo1Bit(inputPath, output1BitPath);
        
        Console.WriteLine("Conversion completed.");
    }
  
    public static void ConvertTo8Bit(string inputPath, string outputPath)
    {
        using (Bitmap bmp = new Bitmap(inputPath))
        {
            using (Bitmap newBmp = new Bitmap(bmp.Width, bmp.Height, PixelFormat.Format8bppIndexed))
            {
                // Create a color palette
                ColorPalette palette = newBmp.Palette;
                for (int i = 0; i < 256; i++)
                {
                    palette.Entries[i] = Color.FromArgb(i, i, i);
                }
                newBmp.Palette = palette;

                // Copy the bitmap data
                for (int y = 0; y < bmp.Height; y++)
                {
                    for (int x = 0; x < bmp.Width; x++)
                    {
                        Color color = bmp.GetPixel(x, y);
                        int gray = (color.R + color.G + color.B) / 3;
                        newBmp.SetPixel(x, y, Color.FromArgb(gray, gray, gray));
                    }
                }
                
                newBmp.Save(outputPath, ImageFormat.Png);
            }
        }
    }
    public static void ConvertTo1Bit(string inputPath, string outputPath)
    {
        using (Bitmap bmp = new Bitmap(inputPath))
        {
            using (Bitmap newBmp = new Bitmap(bmp.Width, bmp.Height, PixelFormat.Format1bppIndexed))
            {
                // Create a color palette
                ColorPalette palette = newBmp.Palette;
                palette.Entries[0] = Color.Black;
                palette.Entries[1] = Color.White;
                newBmp.Palette = palette;

                // Copy the bitmap data
                for (int y = 0; y < bmp.Height; y++)
                {
                    for (int x = 0; x < bmp.Width; x++)
                    {
                        Color color = bmp.GetPixel(x, y);
                        int gray = (color.R + color.G + color.B) / 3;
                        if (gray > 128)
                        {
                            newBmp.SetPixel(x, y, Color.White);
                        }
                        else
                        {
                            newBmp.SetPixel(x, y, Color.Black);
                        }
                    }
                }
                
                newBmp.Save(outputPath, ImageFormat.Png);
            }
        }
    }  
      public static void Convert1BitTo8Bit(string inputPath, string outputPath)
    {
        using (Bitmap bmp = new Bitmap(inputPath))
        {
            // Create a new 8-bit image
            using (Bitmap newBmp = new Bitmap(bmp.Width, bmp.Height, PixelFormat.Format8bppIndexed))
            {
                // Create a grayscale color palette
                ColorPalette palette = newBmp.Palette;
                for (int i = 0; i < 256; i++)
                {
                    palette.Entries[i] = Color.FromArgb(i, i, i);
                }
                newBmp.Palette = palette;

                // Copy the bitmap data
                for (int y = 0; y < bmp.Height; y++)
                {
                    for (int x = 0; x < bmp.Width; x++)
                    {
                        Color color = bmp.GetPixel(x, y);
                        int gray = color.R == 255 ? 255 : 0; // 1-bit black is 0, white is 255
                        newBmp.SetPixel(x, y, Color.FromArgb(gray, gray, gray));
                    }
                }

                newBmp.Save(outputPath, ImageFormat.Png);
            }
        }
    }
}
