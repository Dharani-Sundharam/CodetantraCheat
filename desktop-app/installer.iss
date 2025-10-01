; CodeTantra Automation Desktop App Installer Script
; Inno Setup Script for Windows Installer

#define MyAppName "CodeTantra Automation Pro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CodeTantra Automation"
#define MyAppURL "https://github.com/YOUR_USERNAME/YOUR_REPO"
#define MyAppExeName "CodeTantraAutomation.exe"

[Setup]
; App information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation paths
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=.\installer_output
OutputBaseFilename=CodeTantraAutomation_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Wizard appearance
WizardStyle=modern
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (created by PyInstaller)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Additional files (if any)
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; README and license
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: CreateAppDataFolder

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CreateAppDataFolder();
var
  AppDataPath: String;
begin
  AppDataPath := ExpandConstant('{userappdata}\CodeTantraAutomation');
  
  if not DirExists(AppDataPath) then
  begin
    CreateDir(AppDataPath);
    CreateDir(AppDataPath + '\config');
    CreateDir(AppDataPath + '\logs');
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not IsDotNetInstalled(net45, 0) then
  begin
    MsgBox('This application requires Microsoft .NET Framework 4.5 or higher.'#13#13
      'Please install it and then run this setup again.', mbError, MB_OK);
    Result := False;
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\CodeTantraAutomation"

