package com.wally.mathtutor

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.wally.mathtutor.ui.MathTutorApp
import com.wally.mathtutor.ui.theme.MathTutorTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MathTutorTheme {
                MathTutorApp()
            }
        }
    }
}
