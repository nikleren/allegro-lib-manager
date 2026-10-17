param([string]$Out)
Add-Type -AssemblyName System.Windows.Forms
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Filter = "Access Database (*.accdb;*.mdb)|*.accdb;*.mdb|All Files (*.*)|*.*"
$d.Title = "Select Access Database File"
$d.CheckFileExists = $true
$d.CheckPathExists = $true
$d.Multiselect = $false
$r = $d.ShowDialog()
if ($r -eq [System.Windows.Forms.DialogResult]::OK -and $Out) {
    [System.IO.File]::WriteAllText($Out, $d.FileName, (New-Object System.Text.UTF8Encoding($false)))
}
