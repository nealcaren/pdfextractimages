class Pdfextractimages < Formula
  desc "Extract high-quality images from PDF files while preserving metadata"
  homepage "https://github.com/nealcaren/pdfextractimages"
  url "https://github.com/nealcaren/pdfextractimages/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "b3bcba20ef8c9678260eeb8670cc6f08cc3577426adb608521b97b7b0b16b12d"
  license "MIT"

  depends_on "python@3.8"
  depends_on "astral-sh/uv/uv"

  def install
    bin.install "bin/pdfextractimages"
    bin.install "bin/pdfextractimages_core.py"
  end

  test do
    assert_match "PDF Image Extractor", shell_output("#{bin}/extractpdfimages --help")
  end
end
