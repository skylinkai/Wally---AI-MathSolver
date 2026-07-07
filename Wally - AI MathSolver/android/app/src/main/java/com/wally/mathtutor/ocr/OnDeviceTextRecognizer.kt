package com.wally.mathtutor.ocr

import android.graphics.Bitmap
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.tasks.await

data class LocalOcrResult(
    val text: String,
    val rawText: String,
)

class OnDeviceTextRecognizer {
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    suspend fun recognize(bitmap: Bitmap): LocalOcrResult {
        val image = InputImage.fromBitmap(bitmap, 0)
        val result = recognizer.process(image).await()
        val raw = result.text.replace("\n", " ").trim()
        val normalized = TextNormalizer.normalize(raw)
        return LocalOcrResult(text = normalized.ifBlank { raw }, rawText = raw)
    }
}
