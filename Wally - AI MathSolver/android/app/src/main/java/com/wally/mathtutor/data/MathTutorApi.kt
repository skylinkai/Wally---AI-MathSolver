package com.wally.mathtutor.data

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Query

interface MathTutorApi {
    @GET("health")
    suspend fun health(): HealthResponse

    @POST("solve")
    suspend fun solve(@Body request: SolveRequest): SolveResponse

    @Multipart
    @POST("ocr")
    suspend fun ocr(@Part file: MultipartBody.Part): OCRResponse

    @Multipart
    @POST("solve-image")
    suspend fun solveImage(
        @Part file: MultipartBody.Part,
        @Query("explain") explain: Boolean = true,
    ): SolveResponse
}
