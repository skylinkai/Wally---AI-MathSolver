package com.wally.mathtutor.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Primary,
    onPrimary = Color.White,
    secondary = PrimaryDark,
    background = Surface,
    surface = Color.White,
    onBackground = OnSurface,
    onSurface = OnSurface,
)

@Composable
fun MathTutorTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColors,
        content = content,
    )
}
