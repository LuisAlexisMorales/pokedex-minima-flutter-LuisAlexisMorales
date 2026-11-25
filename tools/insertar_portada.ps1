param(
    [string]$Portada = 'C:\Users\moral\StudioProjects\pokedex_minima\PORTADA_POKEDEX.docx',
    [string]$Cuerpo  = 'C:\Users\moral\StudioProjects\pokedex_minima\CUERPO_INFORME.docx',
    [string]$Salida  = 'C:\Users\moral\StudioProjects\pokedex_minima\INFORME_POKEDEX.docx'
)

# El cuerpo se inserta DENTRO de la portada: al revés se pierde un logo (nota de LEEME.md).
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

try {
    $doc = $word.Documents.Open($Portada)
    $word.Selection.EndKey(6) | Out-Null       # wdStory: ir al final
    $word.Selection.InsertBreak(7) | Out-Null  # wdPageBreak: nueva página
    $word.Selection.InsertFile($Cuerpo) | Out-Null
    $doc.SaveAs2($Salida, 16)                  # wdFormatDocumentDefault (.docx)
    $doc.Close(0)
    Write-Output $Salida
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
