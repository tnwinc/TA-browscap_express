Param(
    [Parameter(Mandatory=$true)][string]$inputFile,
    [Parameter(Mandatory=$true)][string]$outputFile
)
>
clear-host

$data = Get-Content $inputFile
$data | select -Skip 4 | Out-File $ENV:TEMP\temp.csv
Import-CSV $ENV:TEMP\temp.csv -Header $data[2].Replace("`"","") -Delimiter "," | Out-File $ENV:TEMP\temp.txt

$data = Get-Content $ENV:TEMP\temp.txt | select -Skip 4
$data
$data | sort | Get-Unique | out-file $outputFile