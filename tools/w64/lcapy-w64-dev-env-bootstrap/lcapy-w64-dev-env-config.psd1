@{
    ScoopPackages = @(
        @{ Name = "main/ghostscript"; Command = "gs" },
        @{ Name = "main/miktex"; Command = "miktex" },
        @{ Name = "main/imagemagick"; Command = "magick" },
        @{ Name = "main/python"; Command = "python" },
        @{ Name = "main/pipx"; Command = "pipx" },
        @{ Name = "main/git"; Command = "git" }
    )

    PipxPackages = @(
        "jupyterlab",
        "spyder"
    )

    GTK = @{
        Version = "2025.4.0"
        URL     = "https://github.com/wingtk/gvsbuild/releases/download/2025.4.0/GTK3_Gvsbuild_2025.4.0_x64.zip"
        Paths   = @{
            BIN              = "C:\gtk\bin"
            LIB              = "C:\gtk\lib"
            GI_TYPELIB_PATH  = "C:\gtk\lib\girepository-1.0"
            INCLUDE          = @(
                "C:\gtk\include",
                "C:\gtk\include\cairo",
                "C:\gtk\include\glib-2.0",
                "C:\gtk\include\gobject-introspection-1.0",
                "C:\gtk\lib\glib-2.0\include"
            )
        }
    }
}
