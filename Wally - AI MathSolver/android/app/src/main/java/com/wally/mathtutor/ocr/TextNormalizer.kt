package com.wally.mathtutor.ocr

object TextNormalizer {
    /**
     * Mirror of Python text_utils.normalize_ocr_text for ML Kit output.
     */
    fun normalize(raw: String): String {
        var text = raw
        val replacements = mapOf(
            "×" to "*",
            "÷" to "/",
            "−" to "-",
            "–" to "-",
            "—" to "-",
            "²" to "**2",
            "³" to "**3",
            "√" to "sqrt",
            "π" to "pi",
        )
        replacements.forEach { (old, new) -> text = text.replace(old, new) }
        text = text.replace(Regex("\\s+"), "").trim()
        text = text.replace(Regex("(\\d)x")) { "${it.groupValues[1]}*x" }
        text = text.replace(Regex("\\)x")) { ")*x" }
        text = text.replace(Regex("x(\\d)")) { "x*${it.groupValues[1]}" }
        text = text.replace(Regex("(\\d)\\(")) { "${it.groupValues[1]}*(" }
        return text
    }
}
