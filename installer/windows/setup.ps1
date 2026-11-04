#requires -version 5.1
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.IO.Compression.FileSystem
[Windows.Forms.Application]::EnableVisualStyles()
$payload = Join-Path $PSScriptRoot 'files'
$script:worker = $null
$script:operation = ''
$script:logFile = $null
$activation = $null
$script:completed = $false
$engine = Join-Path $PSHOME 'powershell.exe'
try {
    [IO.Compression.ZipFile]::ExtractToDirectory((Join-Path $PSScriptRoot 'payload.zip'), $payload)
    . (Join-Path $payload 'workflow.ps1')
    $manifest = Get-Content -LiteralPath (Join-Path $payload 'manifest.json') -Raw | ConvertFrom-Json
    $activation = New-Object Threading.EventWaitHandle($false,[Threading.EventResetMode]::AutoReset,'Local\HytaleClearViewInstallerActivate')
    $form = New-Object Windows.Forms.Form
    $form.Text = 'Hytale ClearView'
    $form.ClientSize = New-Object Drawing.Size(620,455)
    $form.StartPosition = 'CenterScreen'
    $form.FormBorderStyle = 'FixedDialog'
    $form.MaximizeBox = $false
    $form.Font = New-Object Drawing.Font('Segoe UI',10)
    $form.BackColor = [Drawing.Color]::FromArgb(245,247,250)
    function Label([string]$text,[int]$x,[int]$y,[int]$w,[int]$h) {
        $item=New-Object Windows.Forms.Label
        $item.Text=$text;$item.SetBounds($x,$y,$w,$h);$form.Controls.Add($item)
        return $item
    }
    $title=Label 'Hytale ClearView' 24 20 560 38
    $title.Font=New-Object Drawing.Font('Segoe UI',20,[Drawing.FontStyle]::Bold)
    $null=Label "Versão $($manifest.version) • Controle a neblina pelo painel F9." 26 64 570 28
    $intro=Label 'Este instalador adiciona o ClearView a uma instalação existente do Hytale. Não baixa o jogo. Feche o Hytale antes de continuar.' 26 103 568 45
    $null=Label 'Pasta do Hytale' 26 151 540 24
    $path=New-Object Windows.Forms.TextBox
    $path.SetBounds(26,179,445,29);$path.ReadOnly=$true;$form.Controls.Add($path)
    $browse=New-Object Windows.Forms.Button
    $browse.Text='Localizar…';$browse.SetBounds(481,177,112,32);$form.Controls.Add($browse)
    $status=Label 'Localize o jogo para continuar.' 26 220 565 65
    $progress=New-Object Windows.Forms.ProgressBar
    $progress.SetBounds(26,292,567,22);$progress.Minimum=0;$progress.Maximum=3;$progress.Value=0
    $form.Controls.Add($progress)
    $stageLabel=Label '1. Localizar o jogo   →   2. Instalar   →   3. Concluir' 26 322 565 40
    $rescan=New-Object Windows.Forms.Button
    $rescan.Text='Verificar novamente';$rescan.SetBounds(26,370,180,30);$form.Controls.Add($rescan)

    $install=New-Object Windows.Forms.Button
    $install.Text='Instalar / Atualizar';$install.SetBounds(26,405,180,36);$form.Controls.Add($install)
    $remove=New-Object Windows.Forms.Button
    $remove.Text='Remover';$remove.SetBounds(218,405,110,36);$form.Controls.Add($remove)
    $details=New-Object Windows.Forms.Button
    $details.Text='Ver relatório';$details.SetBounds(340,405,125,36);$details.Enabled=$false;$form.Controls.Add($details)
    $close=New-Object Windows.Forms.Button
    $close.Text='Fechar';$close.SetBounds(477,405,116,36);$form.Controls.Add($close)
    $form.AcceptButton=$install;$form.CancelButton=$close
    function Refresh-Selection {
        $valid=Test-Path -LiteralPath (Join-Path $(if($path.Text){$path.Text}else{$PSScriptRoot}) 'HytaleClient.exe') -PathType Leaf
        $install.Enabled=$valid;$remove.Enabled=$valid
        if($valid){$status.Text='Hytale encontrado. Clique em Instalar / Atualizar para continuar.'}
        else{$status.Text='Hytale não encontrado. Instale o jogo pelo launcher oficial e clique em Verificar novamente. Se já estiver instalado, use Localizar.'}
    }
    function Find-Game {
        $candidates=@(
        (Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'Hytale\install\release\package\game\latest\Client'),
        (Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Hytale\install\release\package\game\latest\Client')
    ) | Where-Object { Test-Path -LiteralPath (Join-Path $_ 'HytaleClient.exe') } | Select-Object -Unique
    if(@($candidates).Count -eq 1){$path.Text=@($candidates)[0]}
        Refresh-Selection
    }
    Find-Game
    $rescan.Add_Click({Find-Game})
    $browse.Add_Click({
        $picker=New-Object Windows.Forms.OpenFileDialog
        $picker.Title='Localize HytaleClient.exe';$picker.Filter='Hytale|HytaleClient.exe'
        try{if($picker.ShowDialog($form) -eq 'OK'){$path.Text=[IO.Path]::GetDirectoryName($picker.FileName);Refresh-Selection}}
        finally{$picker.Dispose()}
    })
    function Start-Operation([string]$operation) {
        if($script:worker -or $script:completed){return}
        if(-not $path.Text -or -not (Test-Path -LiteralPath (Join-Path $path.Text 'HytaleClient.exe') -PathType Leaf)){
            Refresh-Selection
            return
        }
        if(Get-Process -Name HytaleClient -ErrorAction SilentlyContinue){
            [Windows.Forms.MessageBox]::Show($form,'Feche o Hytale e tente novamente. O launcher pode ficar aberto.','Hytale está aberto','OK','Information') | Out-Null
            return
        }
        if($operation -eq 'remove' -and [Windows.Forms.MessageBox]::Show($form,'Remover o ClearView? Seus ajustes serão guardados para uma futura instalação.','Remover ClearView','YesNo','Question') -ne 'Yes'){return}
        try {
            $logRoot=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'ClearView\Logs'
            [IO.Directory]::CreateDirectory($logRoot) | Out-Null
            $script:logFile=Join-Path $logRoot ('setup-'+[Guid]::NewGuid().ToString('N')+'.txt')
            $runner=Join-Path $payload 'operation.ps1'
            $body=New-ClearViewOperation -Engine $engine -Payload $payload -Client $path.Text -Log $script:logFile -Operation $operation
            [IO.File]::WriteAllText($runner,$body,(New-Object Text.UTF8Encoding($true)))
            $start=New-Object Diagnostics.ProcessStartInfo
            $start.FileName=$engine
            $start.Arguments='-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+$runner+'"'
            $start.UseShellExecute=$false;$start.CreateNoWindow=$true
            $script:worker=[Diagnostics.Process]::Start($start)
            $script:operation=$operation
            $progress.Value=0
            $stageLabel.Text='Preparando a operação…'
            foreach($button in @($install,$remove,$browse,$close,$details,$rescan)){$button.Enabled=$false}
            $status.Text=if($operation -eq 'install'){'Verificando o computador e instalando… Aguarde.'}else{'Removendo o ClearView… Aguarde.'}
        }catch{
            [Windows.Forms.MessageBox]::Show($form,'Não foi possível iniciar. Verifique o espaço livre e as permissões da sua conta.','ClearView','OK','Error') | Out-Null
        }
    }
    $install.Add_Click({Start-Operation 'install'})
    $remove.Add_Click({Start-Operation 'remove'})
    $close.Add_Click({$form.Close()})
    $details.Add_Click({if($script:logFile -and (Test-Path -LiteralPath $script:logFile)){Start-Process -FilePath (Join-Path $env:WINDIR 'System32\notepad.exe') -ArgumentList ('"'+$script:logFile+'"')}})
    $timer=New-Object Windows.Forms.Timer
    $timer.Interval=200
    $timer.Add_Tick({
        if($activation -and $activation.WaitOne(0)){
            $form.WindowState=[Windows.Forms.FormWindowState]::Normal
            $form.Show();$form.Activate()
        }
        if($script:worker -and -not $script:worker.HasExited){
            $stageFile=$script:logFile+'.stage'
            $stage=if(Test-Path -LiteralPath $stageFile){Get-Content -LiteralPath $stageFile -Raw -ErrorAction SilentlyContinue}else{''}
            switch(([string]$stage).Trim()){
                '1' {$progress.Value=0;$stageLabel.Text=if($script:operation -eq 'install'){'Etapa 1 de 3: verificando o Hytale e os arquivos do mod.'}else{'Removendo o ClearView…'}}
                '2' {$progress.Value=1;$stageLabel.Text='Etapa 2 de 3: testando a compatibilidade gráfica (até 60 segundos).'}
                '3' {$progress.Value=2;$stageLabel.Text='Etapa 3 de 3: instalando e verificando os arquivos.'}
            }
        }
        if($script:worker -and $script:worker.HasExited){
            $code=$script:worker.ExitCode;$script:worker.Dispose();$script:worker=$null
            foreach($button in @($install,$remove,$browse,$close,$details,$rescan)){$button.Enabled=$true}
            $finished=if(Test-Path -LiteralPath ($script:logFile+'.stage')){(Get-Content -LiteralPath ($script:logFile+'.stage') -Raw).Trim()}else{''}
            if($code -eq 0 -and $finished -eq 'complete'){
                $script:completed=$true
                $progress.Value=3
                $stageLabel.Text=if($script:operation -eq 'install'){'Instalação concluída.'}else{'Remoção concluída.'}
                foreach($button in @($install,$remove,$browse,$rescan)){$button.Enabled=$false}
                $close.Text='Concluir';$form.AcceptButton=$close;$close.Focus() | Out-Null
                $status.Text=if($script:operation -eq 'install'){'Pronto! Abra o Hytale pelo launcher e pressione F9 dentro do jogo.'}else{'ClearView removido. Você pode abrir o Hytale normalmente.'}
            }else{
                $reason='Não foi possível concluir. Clique em Ver relatório para obter ajuda.'
                $report=if(Test-Path -LiteralPath $script:logFile){Get-Content -LiteralPath $script:logFile -Raw}else{''}
                if($report -match 'Feche o Hytale'){$reason='Feche o Hytale e tente novamente.'}
                elseif($report -match 'Outra opengl32|Aurora/ReShade'){$reason='Remova o outro mod de shaders antes de instalar o ClearView.'}
                elseif($report -match 'nao respondeu'){$reason='O teste gráfico não respondeu. A instalação foi interrompida antes de alterar o jogo. Envie o relatório ao suporte.'}
                elseif($report -match 'OpenGL|Smoke test falhou'){$reason='A verificação gráfica falhou. Confira o driver de vídeo e envie o relatório para obter ajuda.'}
                elseif($report -match '1809|64 bits|64 bit'){$reason='Este instalador requer Windows 10 1809 ou superior, de 64 bits.'}
                $stageLabel.Text='Operação não concluída. Você pode tentar novamente ou fechar.'
                Refresh-Selection
                $status.Text=$reason
                [Windows.Forms.MessageBox]::Show($form,$reason,'Não foi possível concluir','OK','Warning') | Out-Null
            }
        }
    })
    $form.Add_Shown({$form.Activate()})
    $form.Add_FormClosing({param($sender,$eventArgs) if($script:worker){
        $eventArgs.Cancel=$true
        $status.Text='Aguarde a operação terminar antes de fechar para preservar os arquivos do jogo.'
    }})
    $timer.Start()
    [Windows.Forms.Application]::Run($form)
    $timer.Stop();$timer.Dispose();$form.Dispose()
} catch {
    [Windows.Forms.MessageBox]::Show('Não foi possível abrir o pacote. Baixe novamente o instalador oficial do ClearView.','ClearView','OK','Error') | Out-Null
    exit 1
} finally {
    if($activation){$activation.Dispose()}
    if(-not $script:worker -and (Test-Path -LiteralPath $payload)){Remove-Item -LiteralPath $payload -Recurse -Force -ErrorAction SilentlyContinue}
}
