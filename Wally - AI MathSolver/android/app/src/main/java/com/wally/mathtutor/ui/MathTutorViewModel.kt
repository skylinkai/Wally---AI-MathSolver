package com.wally.mathtutor.ui

import android.app.Application
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.wally.mathtutor.data.MathTutorRepository
import com.wally.mathtutor.data.SettingsRepository
import com.wally.mathtutor.data.SolveResponse
import com.wally.mathtutor.ocr.OnDeviceTextRecognizer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

data class UiState(
    val equation: String = "",
    val apiUrl: String = "",
    val isLoading: Boolean = false,
    val statusMessage: String? = null,
    val error: String? = null,
    val serverOnline: Boolean? = null,
    val solution: SolveResponse? = null,
    val showSettings: Boolean = false,
    val capturedPreview: Bitmap? = null,
)

class MathTutorViewModel(application: Application) : AndroidViewModel(application) {
    private val settings = SettingsRepository(application)
    private val repository = MathTutorRepository(settings)
    private val textRecognizer = OnDeviceTextRecognizer()

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            settings.apiUrl.collect { url ->
                _uiState.update { it.copy(apiUrl = url) }
            }
        }
        refreshServerStatus()
    }

    fun onEquationChange(value: String) {
        _uiState.update { it.copy(equation = value, error = null) }
    }

    fun toggleSettings() {
        _uiState.update { it.copy(showSettings = !it.showSettings) }
    }

    fun saveApiUrl(url: String) {
        viewModelScope.launch {
            settings.setApiUrl(url)
            _uiState.update { it.copy(showSettings = false) }
            refreshServerStatus()
        }
    }

    fun refreshServerStatus() {
        viewModelScope.launch {
            val online = repository.checkHealth()
            _uiState.update { it.copy(serverOnline = online) }
        }
    }

    fun clearSolution() {
        _uiState.update {
            it.copy(solution = null, error = null, statusMessage = null, capturedPreview = null)
        }
    }

    fun solveTyped() {
        val equation = _uiState.value.equation.trim()
        if (equation.isEmpty()) {
            _uiState.update { it.copy(error = "Enter an equation first.") }
            return
        }
        solve(equation)
    }

    fun onImageSelected(uri: Uri) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null, statusMessage = "Reading image...") }
            try {
                val bytes = readBytes(uri)
                val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                _uiState.update { it.copy(capturedPreview = bitmap) }

                _uiState.update { it.copy(statusMessage = "Running on-device OCR...") }
                val ocr = textRecognizer.recognize(bitmap)
                _uiState.update { it.copy(equation = ocr.text, statusMessage = "Solving with SymPy...") }
                solve(ocr.text)
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(isLoading = false, error = friendlyError(e), statusMessage = null)
                }
            }
        }
    }

    fun solveFromImageServer(uri: Uri) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null, statusMessage = "Uploading to server...") }
            try {
                val bytes = readBytes(uri)
                val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                _uiState.update { it.copy(capturedPreview = bitmap) }
                val result = repository.solveImage(bytes)
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        solution = result,
                        equation = result.detectedProblem,
                        statusMessage = null,
                        error = null,
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(isLoading = false, error = friendlyError(e), statusMessage = null)
                }
            }
        }
    }

    private fun solve(equation: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null, statusMessage = "Solving with SymPy...") }
            try {
                val result = repository.solve(equation)
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        solution = result,
                        statusMessage = null,
                        error = null,
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(isLoading = false, error = friendlyError(e), statusMessage = null)
                }
            }
        }
    }

    private fun readBytes(uri: Uri): ByteArray {
        val resolver = getApplication<Application>().contentResolver
        return resolver.openInputStream(uri)?.use { it.readBytes() }
            ?: throw IOException("Could not read image.")
    }

    private fun friendlyError(e: Exception): String = when (e) {
        is HttpException -> {
            val body = e.response()?.errorBody()?.string()
            body?.takeIf { it.isNotBlank() } ?: "Server error (${e.code()}). Is the API running?"
        }
        is IOException -> "Cannot reach server. Start the API and check Settings → Server URL."
        else -> e.message ?: "Something went wrong."
    }
}
