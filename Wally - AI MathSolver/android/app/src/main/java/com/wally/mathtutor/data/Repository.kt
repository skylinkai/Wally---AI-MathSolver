package com.wally.mathtutor.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.wally.mathtutor.BuildConfig
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

class SettingsRepository(private val context: Context) {
    private val apiUrlKey = stringPreferencesKey("api_url")

    val apiUrl: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[apiUrlKey] ?: BuildConfig.DEFAULT_API_URL
    }

    suspend fun getApiUrl(): String = apiUrl.first()

    suspend fun setApiUrl(url: String) {
        context.dataStore.edit { it[apiUrlKey] = url.trimEnd('/') }
    }
}

class MathTutorRepository(
    private val settings: SettingsRepository,
) {
    private suspend fun api(): MathTutorApi {
        val baseUrl = settings.getApiUrl().let { if (it.endsWith("/")) it else "$it/" }
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
        val client = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .addInterceptor(logging)
            .build()
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(MathTutorApi::class.java)
    }

    suspend fun checkHealth(): Boolean = runCatching {
        api().health().status == "ok"
    }.getOrDefault(false)

    suspend fun solve(equation: String, explain: Boolean = true): SolveResponse {
        return api().solve(SolveRequest(equation = equation, explain = explain))
    }

    suspend fun solveImage(imageBytes: ByteArray, explain: Boolean = true): SolveResponse {
        val body = imageBytes.toRequestBody("image/jpeg".toMediaTypeOrNull())
        val part = MultipartBody.Part.createFormData("file", "photo.jpg", body)
        return api().solveImage(part, explain)
    }
}
