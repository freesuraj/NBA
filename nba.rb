
class Nba < Formula
  desc "Command Line NBA for boxscores, standings and players profile"
  homepage "https://freesuraj.github.io/NBA"
  url "https://github.com/freesuraj/NBA.git", :tag => "0.1"
  head "https://github.com/freesuraj/NBA.git", :branch => "master"

  depends_on :python if MacOS.version <= :snow_leopard

  resource "tabulate" do
    url "https://pypi.python.org/packages/3b/6d/c3e2ba309bfadde4037793b7f48df0d95f52c874b34d2c2b89bf9a966ec3/tabulate-0.7.3.tar.gz"
    sha256 "8a59a61ed6ddfdb009f15917e0f006cc5842f9daa72c519593b7a095e645532a"
  end

  resource "requests" do
    url "https://pypi.python.org/packages/source/r/requests/requests-2.5.1.tar.gz"
    sha256 "7b7735efd3b1e2323dc9fcef060b380d05f5f18bd0f247f5e9e74a628279de66"
  end

  resource "lxml" do
    url "https://pypi.python.org/packages/c4/68/cf0ab7e26de58d14d441f19f7f9c2ab15eb109b0b2640f8b19c1da34e9e0/lxml-3.7.1.tar.gz"
    sha256 "1c7f6771838300787cfa1bb3ed6512e9dc78e60ecb308a8ed49ac956569c1cca"
  end

  include Language::Python::Virtualenv

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/nba", "-h"
  end
end
