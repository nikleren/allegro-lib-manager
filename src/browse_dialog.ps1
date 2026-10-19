param([string]$Out, [string]$Filter = "All Files (*.*)|*.*", [string]$Title = "Select File")
Add-Type -AssemblyName System.Windows.Forms
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Filter = $Filter
$d.Title = $Title
$d.CheckFileExists = $true
$d.CheckPathExists = $true
$d.Multiselect = $false
$r = $d.ShowDialog()
if ($r -eq [System.Windows.Forms.DialogResult]::OK -and $Out) {
    [System.IO.File]::WriteAllText($Out, $d.FileName, (New-Object System.Text.UTF8Encoding($false)))
}
