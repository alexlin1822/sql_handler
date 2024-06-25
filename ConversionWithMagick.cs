using ImageMagick;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;


//Magick.NET-Q8-AnyCPU + ghostscript

namespace PDFtoImage
{
    internal class ConversionWithMagick
    {
        public static void ConvertPdfToBlackWhitePng(string pdfFilePathAndName, string outputPathLandscape, string outputPathPortrait, string tempImagePath, string dpi_str, string threshold_str)
        {
            ConvertPDFToMultipleImages(pdfFilePathAndName, outputPathLandscape, dpi_str);
        }

        public static void ConvertPDFToMultipleImages(string pdfFilePathAndName, string outputPathLandscape,string dpi_str)
        {
            string filename = Path.GetFileNameWithoutExtension(pdfFilePathAndName);

            
            int dpi=Int32.Parse(dpi_str);
            // Settings the density to 300 dpi will create an image with a better quality

            var settings = new MagickReadSettings
            {
                Density = new Density(dpi, dpi)
            };

            var page = 1;
            using (var images = new MagickImageCollection())
            {
                images.Read(pdfFilePathAndName, settings);

                foreach (var image in images)
                {
                    // Convert to black and white using thresholding
                    image.AutoLevel(); // Adjust contrast for better thresholding
                    image.Threshold(new Percentage(50)); // 50% threshold for black and white

                    // Set background color to white
                    image.BackgroundColor = MagickColors.White;

                    // Set format to 1-bit PNG
                    image.Format = MagickFormat.Png8; // PNG8 is for 1-bit PNG
                    image.SetBitDepth(1);

                    image.Write(outputPathLandscape + "\\" +filename+"_" + page + "Landscape.png");
                    page++;
                }
            }
        }
    }
}
