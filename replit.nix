{ pkgs }: {
  deps = [
    pkgs.openssh
    pkgs.openssl
    pkgs.postgresql
    pkgs.glibcLocales
    pkgs.geckodriver
    pkgs.ungoogled-chromium
    pkgs.chromedriver
  ];
}
