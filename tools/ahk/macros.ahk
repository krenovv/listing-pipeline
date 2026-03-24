#Requires AutoHotkey v2.0

; Дополнительные макросы для ускорения ручной работы
; при создании и обработке лотов.

SetKeyDelay(50, 50)
SendMode("Input")


; ==============
; HTML Templates
; ==============

!1::{  ; Артикул (HTML блок)
    ClipSaved := A_Clipboard
    A_Clipboard := '<p><span style="color:#808080;"><strong>Артикул: </strong></span></p>' "`r`n`r`n"

    Sleep(10)
    Send("^v")
    Sleep(10)
    Send("{Alt up}{Ctrl up}{Shift up}")

    A_Clipboard := ClipSaved
}


!2::{  ; YouTube iframe (код берётся из буфера)
    ClipSaved := A_Clipboard
    code := A_Clipboard

    A_Clipboard := '<iframe width="807" height="454" src="https://www.youtube.com/embed/' code '" frameborder="0"></iframe>' "`r`n`r`n"

    Sleep(10)
    Send("^v")
    Sleep(10)
    Send("{Alt up}{Ctrl up}{Shift up}")

    A_Clipboard := ClipSaved
}


!3::{  ; Размер: <значение из буфера>
    ClipSaved := A_Clipboard
    text := A_Clipboard

    A_Clipboard := '<p><strong><span style="font-size:14pt;">Размер: ' text '</span></strong></p>' "`r`n`r`n"

    Sleep(10)
    Send("^v")
    Sleep(10)
    Send("{Alt up}{Ctrl up}{Shift up}")

    A_Clipboard := ClipSaved
}


!4::{  ; Гарантированно природный камень
    ClipSaved := A_Clipboard

    A_Clipboard := '<p><strong><span style="font-size:14pt;">Гарантированно природный камень.</span></strong></p>' "`r`n`r`n"

    Sleep(10)
    Send("^v")
    Sleep(10)
    Send("{Alt up}{Ctrl up}{Shift up}")

    A_Clipboard := ClipSaved
}


!5::{  ; Сертификат соответствия
    ClipSaved := A_Clipboard

    A_Clipboard := '<p><strong><span style="font-size:14pt;">Сертификат соответствия от дилера прилагается бесплатно.</span></strong></p>' "`r`n`r`n"

    Sleep(10)
    Send("^v")
    Sleep(10)
    Send("{Alt up}{Ctrl up}{Shift up}")

    A_Clipboard := ClipSaved
}


!SC029::{  ; Быстрая вставка ".jpg"
    ClipSaved := A_Clipboard

    A_Clipboard := ".jpg"

    Sleep(10)
    Send("^v")
    Sleep(10)
    Send("{Alt up}")

    A_Clipboard := ClipSaved
}


; =============
; Text Snippets
; =============

:*:тг1::{
    SendInput "И еще, если вдруг на Мешке не получите ответ на Ваше сообщение в течение 3 дней, то, пожалуйста, напишите нам на адрес электронной почты или в Telegram (они указаны в первом сообщении по сделке). Там ответ поступает гарантированно в течение 1-2 рабочих дней. Много сообщений, из-за чего некоторые могут теряться."
}


:*:ср1::{
    SendInput "Сроки отправки лотов указаны в описании, они составляют до 6-8 недель, срок зависит от отправки дилером, затем работы таможни и почты. Вероятнее всего, прибудут к [X], можете уточнить к этому моменту. И еще, если вдруг на Мешке не получите ответ на Ваше сообщение в течение 3 дней, то, пожалуйста, напишите нам на адрес электронной почты или в Telegram (они указаны в первом сообщении по сделке). Там ответ поступает быстрее. Много сообщений, из-за чего некоторые могут теряться."
}


; ==========
; Navigation
; ==========

; Переключение виртуальных рабочих столов
!Left::{
    Send("^#{Left}")
    Send("{Alt up}")
}

!Right::{
    Send("^#{Right}")
    Send("{Alt up}")
}


; Переключение вкладок (только Chrome)
^CapsLock::{
    SetCapsLockState "Off"

    if WinActive("ahk_exe chrome.exe") {
        Send("^+{Tab}")
    }
}


; =========================
; Context-dependent actions
; =========================

^SC029::{  ; Ctrl + ё → "Оплачен" с разным поведением
    if WinActive("ahk_exe EXCEL.EXE") {
        Send("Оплачен{Enter}")
    }
    else if WinActive("ahk_exe chrome.exe") {
        Send("Оплачен^{Enter}")
    }
    else {
        Send("Оплачен{Enter}")
    }

    Send("{Alt up}")
}