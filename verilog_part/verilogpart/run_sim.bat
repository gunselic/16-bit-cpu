@echo off
echo ------------------------------------------------
echo CPU Simulation Logic - Otomatik Sinyal Modu
echo ------------------------------------------------
echo.

REM PATH ayarina C:\iverilog\bin klasoru ekleniyor...
set "PATH=%PATH%;C:\iverilog\bin;C:\iverilog\gtkwave\bin"

echo [1] 'iverilog' komutu kontrol ediliyor...
iverilog -V >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] 'iverilog' kontrolunde hata alindi ama devam edilecek.
)

echo.
echo [2] Kodlar derleniyor...
iverilog -o cpu_sim.vvp tb_cpu.v cpu.v pc.v sign_extend.v alu.v control_unit.v register_file.v pipeline_reg.v instruction_memory.v data_memory.v hazard_detection.v forwarding_unit.v

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Derleme sirasinda hata olustu.
    pause
    exit /b 1
)

echo.
echo [3] Simulasyon calistiriliyor...
vvp cpu_sim.vvp

echo.
echo [4] GTKWave aciliyor (Sinyaller hazir gelecek)...
REM GTKWave'i signals.gtkw ile aciyoruz
where gtkwave >nul 2>nul
if %errorlevel% equ 0 (
    start gtkwave cpu_wave.vcd signals.gtkw
) else (
    if exist "C:\iverilog\gtkwave\bin\gtkwave.exe" (
        start "" "C:\iverilog\gtkwave\bin\gtkwave.exe" cpu_wave.vcd signals.gtkw
    ) else if exist "C:\iverilog\bin\gtkwave.exe" (
        start "" "C:\iverilog\bin\gtkwave.exe" cpu_wave.vcd signals.gtkw
    ) else (
        echo [UYARI] GTKWave bulunamadi. cpu_wave.vcd ve signals.gtkw dosyalarini manuel acin.
    )
)

echo.
echo ISLEM BASARIYLA TAMAMLANDI.
pause
