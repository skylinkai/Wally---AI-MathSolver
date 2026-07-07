package com.wally.mathtutor.data

import com.google.gson.annotations.SerializedName

data class SolveRequest(
    val equation: String,
    val explain: Boolean = true,
)

data class StepDto(
    val title: String,
    val content: String,
)

data class SolveResponse(
    @SerializedName("problem_type") val problemType: String,
    @SerializedName("detected_problem") val detectedProblem: String,
    @SerializedName("normalized_expression") val normalizedExpression: String,
    val steps: List<StepDto>,
    val solutions: List<String>,
    val verified: Boolean,
    @SerializedName("verification_detail") val verificationDetail: String,
    val explanation: String,
)

data class OCRResponse(
    val text: String,
    val confidence: Double,
)

data class HealthResponse(
    val status: String,
)
