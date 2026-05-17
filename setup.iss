; setup.iss
; =========
; Inno Setup installer skript za Talas Downloader
;
; Kako koristiti:
; 1. Instaliraj Inno Setup sa: https://jrsoftware.org/isdl.php
; 2. Otvori ovaj fajl u Inno Setup Compileru
; 3. Klikni Build -> Compile (ili Ctrl+F9)
; 4. Dobićeš TalasDownloaderSetup.exe u Output/ folderu

#define MyAppName "Talas Downloader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Talas App"
#define MyAppURL "https://github.com/tvoj-username/TalasDownloader"
#define MyAppExeName "TalasDownloader.exe"
; Putanja do build foldera (promeni prema svom računaru)
#define MySourceDir "dist\TalasDownloader"

[Setup]
; Jedinstveni ID aplikacije — NEMOJ menjati posle prvog release-a
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Default install folder
DefaultDirName={autopf}\{#MyAppName}

; Start Menu grupa
DefaultGroupName={#MyAppName}
AllowNoIcons=no

; Putanja do output foldera za setup.exe
OutputDir=Output
OutputBaseFilename=TalasDownloaderSetup
SetupIconFile=assets\icon.ico

; Kompresija — lzma daje manji fajl
Compression=lzma2/ultra64
SolidCompression=yes

; Minimalana verzija Windows-a
MinVersion=10.0

; 64-bit
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Prikaz u Add/Remove Programs
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Prikaži progress dialog
ShowLanguageDialog=no
LanguageDetectionMethod=none

; Wizard stil — moderan
WizardStyle=modern
WizardResizable=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Desktop shortcut — opciono
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Kopiraj ceo build folder u install dir
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"

; Desktop shortcut (samo ako korisnik odabere)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

; Start Menu — Uninstall
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
; Ponudi pokretanje posle instalacije
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Obriši logs, cache i temp pri deinstalaciji
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\cache"
Type: filesandordirs; Name: "{app}\temp"

[Code]
// Proveri da li je aplikacija već instalirana i pokrenuta
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
