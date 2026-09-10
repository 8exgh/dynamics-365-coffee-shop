[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [switch] $AcceptEula,
    [string] $ContainerName = 'bc-coffee',
    [string] $ArtifactVersion = '28.5',
    [ValidateSet('process', 'hyperv')]
    [string] $Isolation = 'process',
    [PSCredential] $Credential,
    [switch] $RunTests
)

$ErrorActionPreference = 'Stop'
if (-not $AcceptEula) { throw 'Pass -AcceptEula after reviewing the Microsoft Business Central container license terms.' }
if ($env:OS -ne 'Windows_NT') { throw 'Business Central containers require a Windows Docker host.' }
if ((docker info --format '{{.OSType}}') -ne 'windows') { throw 'Switch Docker to Windows containers before running this script.' }
if (-not $Credential) { $Credential = Get-Credential -UserName 'coffeeadmin' -Message 'Choose the Business Central sandbox administrator password' }
if (-not (Get-Module -ListAvailable BcContainerHelper)) { Install-Module BcContainerHelper -Scope CurrentUser -Force }
Import-Module BcContainerHelper
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$Workspace = Join-Path $env:ProgramData 'BcContainerHelper\CoffeeShop'
New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
foreach ($Folder in @('business-central', 'business-central-tests')) {
    $Destination = Join-Path $Workspace $Folder
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item (Join-Path $ProjectRoot "$Folder\app.json") $Destination -Force
    Copy-Item (Join-Path $ProjectRoot "$Folder\src") $Destination -Recurse -Force
}
$Existing = docker ps -a --format '{{.Names}}' | Where-Object { $_ -eq $ContainerName }
if (-not $Existing) {
    $Artifact = Get-BcArtifactUrl -type Sandbox -country w1 -version $ArtifactVersion -select Latest
    if (-not $Artifact) { throw "No W1 sandbox artifact found for version $ArtifactVersion." }
    $Parameters = @{
        accept_eula = $true
        containerName = $ContainerName
        artifactUrl = $Artifact
        auth = 'UserPassword'
        Credential = $Credential
        updateHosts = $true
        includeAL = $true
        memoryLimit = '8G'
        isolation = $Isolation
        accept_outdated = $true
        restart = 'unless-stopped'
    }
    if ($RunTests) { $Parameters.includeTestToolkit = $true; $Parameters.includeTestLibrariesOnly = $true }
    New-BcContainer @Parameters
}
$Companies = Get-CompanyInBcContainer -containerName $ContainerName
if (-not ($Companies | Where-Object { $_.CompanyName -eq 'Eight Examples Coffee' -or $_.Name -eq 'Eight Examples Coffee' })) {
    New-CompanyInBcContainer -containerName $ContainerName -companyName 'Eight Examples Coffee' -evaluationCompany
}
$App = Compile-AppInBcContainer -containerName $ContainerName -credential $Credential -appProjectFolder (Join-Path $Workspace 'business-central')
Publish-BcContainerApp -containerName $ContainerName -appFile $App -skipVerification -sync -install -upgrade -ignoreIfAppExists
Invoke-NavContainerCodeunit -containerName $ContainerName -CompanyName 'Eight Examples Coffee' -Codeunitid 50100
if ($RunTests) {
    $TestApp = Compile-AppInBcContainer -containerName $ContainerName -credential $Credential -appProjectFolder (Join-Path $Workspace 'business-central-tests')
    Publish-BcContainerApp -containerName $ContainerName -appFile $TestApp -skipVerification -sync -install -upgrade -ignoreIfAppExists
    $Passed = Run-TestsInBcContainer -containerName $ContainerName -credential $Credential -companyName 'Eight Examples Coffee' -extensionId 'c34ecdd3-b619-4ea8-9fd9-ccca33769a59' -returnTrueIfAllPassed -detailed -XUnitResultFileName (Join-Path $Workspace 'coffee-tests.xml')
    if (-not $Passed) { throw 'Business Central integration tests failed. Review coffee-tests.xml.' }
}
Invoke-NavContainerCodeunit -containerName $ContainerName -CompanyName 'Eight Examples Coffee' -Codeunitid 50101
Write-Host "Business Central: http://$ContainerName/BC/?company=Eight%20Examples%20Coffee"
Write-Host 'Choose Coffee Shop Manager in My Settings. Open Coffee Shop Setup to review configuration.'
