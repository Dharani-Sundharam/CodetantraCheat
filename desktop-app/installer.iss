; CodeTantra Automation Desktop App Installer Script
; Inno Setup Script for Windows Installer

#define MyAppName "CodeTantra Automation Pro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CodeTantra Automation"
#define MyAppURL "https://github.com/CodeTantraAutomation"
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

; README and documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{app}\..\README.md'))

; Configuration files
Source: "..\config.py"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{app}\..\config.py'))
Source: "..\credentials.py"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{app}\..\credentials.py'))
Source: "..\comment_remover.py"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{app}\..\comment_remover.py'))

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
  // No special requirements for Python-based application
end;

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\CodeTantraAutomation"

