class Pdfextractimages < Formula
  desc "Extract high-quality images from PDF files while preserving metadata"
  homepage "https://github.com/nealcaren/pdfextractimages"
  url "https://github.com/nealcaren/pdfextractimages/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "THE_ACTUAL_SHA256_YOU_GENERATED"
  license "MIT"

  depends_on "python@3.8"
  depends_on "astral-sh/uv/uv"

  def install
    bin.install "bin/extractpdfimages"
    bin.install "bin/pdfextractimages.py"
  end

  test do
    assert_match "PDF Image Extractor", shell_output("#{bin}/extractpdfimages --help")
  end
end
