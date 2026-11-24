# Resident Evil Code: Veronica X HD — Android launcher settings

This document tracks the requested launcher redesign for the Android ARM64 build. The known-good game launch path from Workflow #26 must remain intact while the launcher is replaced.

## Visual target
- Use the user-approved 16:9 launcher/settings artwork (Claire and Steve, blue-black background, red illuminated borders and controls) as the visual reference.
- Do not use the artwork as the only UI. Buttons, tabs, selectors, sliders and toggles must be real Android controls layered in a responsive layout.
- Use landscape for the launcher and game where required by the title; verify existing SDL orientation before changing the game activity.
- Keep the game title, logo and red/black identity. Do not show SDL sample/demo text or controls.

## Launcher navigation
- Iniciar Jogo: retain Workflow #26 behavior. If the private game copy is already prepared, launch GameSDLActivity with the same game-root argument. Otherwise open SAF folder selection and copy/validate Default.xex before launch.
- Configurações: open settings with tabs for Gráficos, Desempenho, Controles and Áudio.
- Controles: expose physical-controller status, touch-control visibility policy, layout editor, size and opacity.
- Salvar / Carregar: reserve for actual supported save-state functionality; do not present a nonfunctional button as working.
- Informações and Sair: implement as real actions.

## Requested graphics controls
- Output resolution: 720p, 900p, 1080p (only modes supported by the Android display/surface).
- Render scale: native / lower scales only where the renderer supports them.
- Image quality: economy, balanced, high.
- Image filter: bilinear, CAS, FSR; only expose filters compiled and available on this Android build.
- FSR mode: Quality, Balanced, Performance; only when FSR is integrated and initialized.
- CAS sharpness slider; only when CAS is integrated.
- Anti-aliasing: only modes actually implemented by the current renderer.
- Particle/effect quality: only if the game/runtime exposes a working control.
- Aspect ratio: automatic / preserve aspect ratio, only if supported.

## Requested performance controls
- FPS cap: 30, 45, 60, restricted to supported frame pacing modes.
- V-Sync: enabled/disabled only if the presenter exposes a reliable setting.
- FPS counter: show/hide; use the existing presented-FPS JNI path.
- Shader cache: enable/disable only if a real cache setting exists.
- Reduce heavy effects: map to a verified game/runtime setting; do not silently fake it.

## Requested controller controls
- Physical Bluetooth/gamepad input must work alongside the virtual touch gamepad.
- Auto touch visibility: hide touch overlay only after a physical controller is detected and confirmed to deliver input; show it again after disconnect/idle policy.
- Manual policies: Automatic / Always show / Always hide.
- Layout editor: drag each touch control; adjust size and opacity; save positions in app preferences; restore defaults.
- Editing mode must not send game button presses.
- Do not treat the virtual touch gamepad as a physical controller when deciding whether to hide the overlay.

## Audio controls
- Master/music/effects sliders only if there are real runtime/game audio controls. Persist settings only after a verified mapping exists.

## Persistence and application
- Persist user selections in app-private SharedPreferences (or a versioned app-private settings file).
- Clearly mark settings that require restarting the game.
- Provide Apply and Restore defaults actions.
- Pass settings into the runtime only through verified ReXGlue/game cvars or documented Android hooks. A saved UI value alone is not a functional setting.
- Keep unsupported controls disabled with a short explanation until implementation is complete.

## Verification gates before producing the next user-test APK
1. Launcher artwork and layout are legible in landscape on the Motorola Edge 30 Pro.
2. Start button still opens the already-prepared game from Workflow #26.
3. SAF selection/copy and XEX2 validation still work for a first launch.
4. Preferences survive force-close and relaunch.
5. Each enabled option changes real runtime/game behavior; unsupported options remain disabled.
6. Bluetooth controller is enumerated by Android, reaches SDL/ReXGlue, and controls the game.
7. Automatic touch hiding occurs only after physical-controller input is confirmed; touch controls return after disconnect.
8. Touch layout changes persist, and editor mode does not send game input.
9. APK package/ABI/signature checks pass and private game files are not included in the APK or public artifacts.

## Current known baseline
- Workflow #26 opens the game successfully on the user's phone.
- The installer now generates a separate native `GameSettingsActivity` with Gráficos, Desempenho, Controles and Áudio sections, a 720p/1080p output-mode selector (1080p default), FPS-counter toggle, and touch-overlay policy selector. The setup screen opens this settings page without changing the existing SAF copy/launch path.
- The selected output mode is passed to ReXGlue as `window_width` / `window_height`; the current image effect is explicitly `bilinear`. The FPS preference controls the on-screen readout. Automatic touch mode hides the overlay only after a physical key/joystick event is received and restores it after controller removal.
- The new settings screen is an initial functional implementation, not yet a pixel-matched recreation of the approved red/black artwork. FSR/CAS, render scaling, AA, FPS cap, V-Sync, shader cache, effects and audio controls remain unavailable/disabled because the Android runtime does not yet expose verified working hooks for them.
- Touch overlay code exists, but the user's prior test reported that only on-screen controls worked; Bluetooth was not working.
- The presented-FPS JNI path exists in the game activity, but it must be revalidated in the actual next APK.
- FSR/CAS, resolution scaling, AA, shader cache, heavy-effect controls and audio sliders must not be claimed as working until mapped to real Android runtime/game settings.

## Verified ReXGlue option mapping (SDK source inspection)

The pinned ReXGlue SDK declares these presenter cvars:
- present_effect: bilinear, cas, fsr, fsr2, fsr3 only when RE​​X_HAS_FIDELITYFX_SDK is compiled; otherwise bilinear is the only allowed value.
- present_cas_additional_sharpness: CAS sharpness, only with FidelityFX SDK support.
- present_fsr_quality_mode: auto, nativeaa, quality, balanced, performance, ultra_performance, only with FidelityFX SDK support.
- present_fsr_max_upsampling_passes and present_fsr_sharpness_reduction: FSR tuning, only with FidelityFX SDK support.
- present_letterbox, present_safe_area_x/y, present_dither, present_allow_overscan_cutoff.
- window_width, window_height, fullscreen and resolution are declared by the SDK; actual Android surface behavior still needs device validation.
- Vulkan exposes allow-present-mode switches (immediate, mailbox, FIFO relaxed); these are not equivalent to a user-selectable exact FPS cap.

The current private Android workflow explicitly passes -DREXGLUE_ENABLE_FIDELITYFX=OFF. Therefore this APK configuration cannot honestly offer CAS/FSR yet: the current presenter is limited to bilinear. The shader source files being present in the SDK does not mean the FidelityFX SDK/runtime is enabled in this Android build.

No FPS-cap, shader-cache, particle-quality, reduced-effects, anti-aliasing or game-audio cvar was found in the inspected SDK flags/presenter sources. These controls must remain disabled or be implemented through verified game-specific hooks. The already-added presented-FPS counter is a readout, not a frame limiter.


## Correções após avaliação do APK #28 — 2026-11-08

- O usuário confirmou que o APK #28 ainda não corresponde à referência visual aprovada.
- Commit `d390337051baa069ddd1757304c7ab8e4eecf313`: o instalador agora copia a arte fornecida também como `drawable/recvx_icon.png`, usa essa imagem diretamente no cabeçalho da tela inicial e atualiza os XMLs de ícone adaptativo do Android 8+ para não deixar os recursos adaptativos SDL sobreporem os PNGs.
- Commit `ee9c0f14fac43c4578090920cd51e64038e97dc3`: ajustes de espaçamento, hierarquia tipográfica e seletores escuros na tela de configurações, aproximando a apresentação da identidade vermelha/preta da referência.
- Estes commits ainda precisam passar pelo smoke test Android e por uma compilação privada completa antes de gerar APK para o usuário.
- O editor de controles táteis com arrastar/soltar, persistência de posições e tamanho/opacidade continua pendente; não apresentar como implementado.
- O funcionamento do controle Bluetooth continua pendente de confirmação no aparelho. O modo automático de ocultação deve continuar condicionado à entrada física confirmada, e nunca apenas à enumeração do gamepad virtual.
- Os controles de renderização, FSR/CAS, limite de FPS, V-Sync, cache, efeitos e áudio só devem ser habilitados após integração com hooks reais do runtime.


## Drivers Vulkan personalizados — análise dos pacotes recebidos (2026-11-24)

### Pacotes analisados
- Turnip v26.0.0 R7 (padrão), GMEM e SYSMEM.
- Estrutura de cada ZIP: `meta.json` + `vulkan.ad07xx.so`; ELF ARM64/AArch64; Vulkan 1.4.335; minApi 27.
- O binário padrão e o SYSMEM são idênticos; GMEM é um binário distinto. A interface deve identificar claramente as variantes sem sugerir que padrão e SYSMEM têm código diferente.

### Requisito de implementação
A seção Drivers deve prever driver do sistema (padrão), importar ZIP, listar pacotes, selecionar, remover e indicar o driver ativo. A importação deve validar ZIP, metadados, nome da biblioteca, ELF ARM64 e integridade antes de copiar para diretório privado do aplicativo. Nunca executar conteúdo arbitrário do ZIP nem copiar drivers para o repositório público.

### Bloqueio antes de declarar seleção funcional
O loader Vulkan Android usa a descoberta HAL do sistema (`hw_get_module("vulkan")`) e não permite que um APK comum substitua o driver do sistema por uma biblioteca colocada no armazenamento privado. Portanto, a UI não pode marcar um pacote Turnip como “ativo” só porque foi importado ou selecionado.

Investigar a extensão `VK_LUNARG_direct_driver_loading` como caminho de carregamento direto fornecido pela aplicação. Antes de implementar ativação, confirmar que o loader Vulkan do dispositivo expõe a extensão, que a biblioteca Turnip pode ser carregada nesse modo e que a criação de instância do ReXGlue aceita o driver externo. Se não for suportado, deixar a ativação desabilitada e explicar a limitação; manter “Driver do sistema” como única opção ativa. Não usar `VK_DRIVER_FILES` como solução Android sem evidência, pois a descoberta Android documentada é diferente.

### Critérios de aceitação
1. Importação segura e persistente dos três pacotes.
2. Remoção e seleção persistentes, com indicação separada de “importado/selecionado” e “realmente carregado”.
3. Log de inicialização confirmando o driver Vulkan efetivamente carregado (nome/versão/driverID quando disponível).
4. Fallback automático ao driver do sistema se o carregamento direto falhar; nunca deixar o app sem caminho de inicialização.
5. Não habilitar o botão “Ativar” até os itens 2–4 estarem comprovados no Motorola Edge 30 Pro.


## Revisão do plano — usar libadrenotools (referência NFSMW-Recompiled-Mobile)

A conclusão anterior de que um APK Android comum não poderia carregar Turnip foi corrigida. A referência https://github.com/victorgbd/NFSMW-Recompiled-Mobile implementa carregamento de driver Vulkan customizado sem substituir o driver do sistema, usando libadrenotools.

### Implementação a portar para o RECVX
- Importador Java: ler `meta.json`, usar o `libraryName` exato e extrair a biblioteca para `files/gpu_drivers/<driver>/` no armazenamento interno privado. Não extrair caminhos arbitrários do ZIP; validar biblioteca, tamanho e ELF ARM64.
- Preferência persistente para driver do sistema ou driver importado; listar, selecionar e remover na launcher.
- No processo do jogo, passar `--android_native_lib_dir`, `--android_tmp_dir`, `--android_gpu_driver_dir` e `--android_gpu_driver_name` como cvars init-only.
- Integrar libadrenotools no SDK Android e alterar `VulkanInstance::Create`: chamar `adrenotools_open_libvulkan(RTLD_NOW, ADRENOTOOLS_DRIVER_CUSTOM, ...)`, adotar o handle no DynamicLibrary e manter fallback para o driver do sistema se falhar.
- Empacotar as bibliotecas hooks necessárias em `nativeLibraryDir`; revisar `useLegacyPackaging = true`/equivalente no Gradle para que as .so sejam extraídas.
- Garantir que o log diferencie “driver escolhido”, “driver customizado carregado” e “fallback para driver do sistema”.

### Cuidados para os pacotes fornecidos
- Ler o `libraryName` de cada `meta.json`; não assumir `libvulkan_freedreno.so` nem renomear `vulkan.ad07xx.so`.
- Manter padrão, GMEM e SYSMEM como opções identificáveis. Binários padrão e SYSMEM dos ZIPs recebidos foram identificados como idênticos; GMEM é diferente.
- Não habilitar turbo KGSL automaticamente; testar desligado primeiro.
- A referência NFSMW documenta que Turnip Gen8 V36 no Adreno 830 só inicia com `TU_DEBUG=sysmem` e foi mais lento que Qualcomm (44 vs 60 FPS), enquanto GMEM travou. Isso é evidência do aparelho de referência, não previsão para o Edge 30 Pro/Adreno 730 ou Turnip R7.

### Validação obrigatória
1. Compilar e executar primeiro com driver Qualcomm do sistema (sem regressão).
2. Confirmar que os hooks do adrenotools estão no APK e são encontrados no `nativeLibraryDir`.
3. Testar importação e seleção de cada ZIP R7 no Edge 30 Pro.
4. Confirmar no log o nome/versão do driver realmente carregado; se falhar, confirmar fallback.
5. Comparar estabilidade, sombras, FPS e temperatura entre sistema e cada variante.
6. Só depois considerar a integração concluída; nenhuma importação de ZIP, isoladamente, prova que o driver está ativo.

**Referência de código:** `tools/parche_turnip.py`, `android/app/src/main/java/io/github/nfsmwrecomp/Drivers.java`, `Ajustes.java`, `SetupActivity.java` e `docs/android.md` no repositório NFSMW-Recompiled-Mobile.


## Implementação em andamento — integração do Turnip no SDK (2026-11-24)

- Patch do SDK: `scripts/ensure-rexglue-turnip.py`.
- Workflow: `.github/workflows/android-arm64-probe.yml` agora clona libadrenotools no commit `8fae8ce254dfc1344527e05301e43f37dea2df80` e executa o patch após os patches Android.
- SDK fixado: `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb`.
- O patch prepara o carregamento nativo via `adrenotools_open_libvulkan` e fallback ao driver do sistema. Ainda não há confirmação de compilação; aguardar workflow.
- Não confundir esta etapa com a feature completa: importação ZIP, seleção persistente, empacotamento das hooks no APK e passagem das cvars pela launcher ainda faltam.
- A referência NFSMW usa `useLegacyPackaging = true` porque as hooks precisam existir em `nativeLibraryDir`; reproduzir isso no APK real e validar nomes dos artefatos gerados.
