package com.wally.mathtutor.ui

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.net.Uri
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Cloud
import androidx.compose.material.icons.filled.PhotoLibrary
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import com.wally.mathtutor.data.SolveResponse
import com.wally.mathtutor.ui.theme.Error
import com.wally.mathtutor.ui.theme.Success
import java.io.File

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MathTutorApp(viewModel: MathTutorViewModel = viewModel()) {
    val state by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    var cameraUri by remember { mutableStateOf<Uri?>(null) }

    val galleryLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri -> uri?.let { viewModel.onImageSelected(it) } }

    val cameraLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.TakePicture()
    ) { success ->
        if (success) cameraUri?.let { viewModel.onImageSelected(it) }
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            val file = File(context.cacheDir, "capture_${System.currentTimeMillis()}.jpg")
            val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)
            cameraUri = uri
            cameraLauncher.launch(uri)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("AI Math Tutor") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    actionIconContentColor = MaterialTheme.colorScheme.onPrimary,
                ),
                actions = {
                    IconButton(onClick = { viewModel.toggleSettings() }) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings")
                    }
                },
            )
        },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            ServerStatusBadge(online = state.serverOnline, apiUrl = state.apiUrl)

            if (state.showSettings) {
                SettingsCard(
                    apiUrl = state.apiUrl,
                    onSave = viewModel::saveApiUrl,
                    onTest = viewModel::refreshServerStatus,
                )
            }

            Text(
                "Take a photo or type a math problem",
                style = MaterialTheme.typography.titleMedium,
            )

            Text(
                text = "By Arindam Chakraborty",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(
                    onClick = {
                        val granted = ContextCompat.checkSelfPermission(
                            context, Manifest.permission.CAMERA
                        ) == PackageManager.PERMISSION_GRANTED
                        if (granted) {
                            val file = File(context.cacheDir, "capture_${System.currentTimeMillis()}.jpg")
                            val uri = FileProvider.getUriForFile(
                                context, "${context.packageName}.fileprovider", file
                            )
                            cameraUri = uri
                            cameraLauncher.launch(uri)
                        } else {
                            permissionLauncher.launch(Manifest.permission.CAMERA)
                        }
                    },
                    modifier = Modifier.weight(1f),
                ) {
                    Icon(Icons.Default.CameraAlt, null, Modifier.size(18.dp))
                    Spacer(Modifier.size(8.dp))
                    Text("Camera")
                }
                FilledTonalButton(
                    onClick = { galleryLauncher.launch("image/*") },
                    modifier = Modifier.weight(1f),
                ) {
                    Icon(Icons.Default.PhotoLibrary, null, Modifier.size(18.dp))
                    Spacer(Modifier.size(8.dp))
                    Text("Gallery")
                }
            }

            state.capturedPreview?.let { bitmap ->
                Image(
                    bitmap = bitmap.asImageBitmap(),
                    contentDescription = "Captured problem",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(160.dp),
                    contentScale = ContentScale.Crop,
                )
            }

            OutlinedTextField(
                value = state.equation,
                onValueChange = viewModel::onEquationChange,
                label = { Text("Equation") },
                placeholder = { Text("e.g. 2*x**2 + 5*x - 3 = 0") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = false,
                minLines = 2,
                textStyle = MaterialTheme.typography.bodyLarge.copy(fontFamily = FontFamily.Monospace),
            )

            Button(
                onClick = viewModel::solveTyped,
                enabled = !state.isLoading,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("Solve")
            }

            if (state.isLoading) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    CircularProgressIndicator(modifier = Modifier.size(24.dp))
                    Spacer(Modifier.size(12.dp))
                    Text(state.statusMessage ?: "Working...")
                }
            }

            state.error?.let { msg ->
                Card(colors = CardDefaults.cardColors(containerColor = Error.copy(alpha = 0.1f))) {
                    Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Warning, null, tint = Error)
                        Spacer(Modifier.size(8.dp))
                        Text(msg, color = Error)
                    }
                }
            }

            state.solution?.let { solution ->
                SolutionCard(solution)
                OutlinedButton(onClick = viewModel::clearSolution, modifier = Modifier.fillMaxWidth()) {
                    Text("Solve another problem")
                }
            }
        }
    }
}

@Composable
private fun ServerStatusBadge(online: Boolean?, apiUrl: String) {
    val (color, icon, label) = when (online) {
        true -> Triple(Success, Icons.Default.CheckCircle, "Server connected")
        false -> Triple(Error, Icons.Default.Warning, "Server offline — start API on $apiUrl")
        null -> Triple(MaterialTheme.colorScheme.onSurface, Icons.Default.Cloud, "Checking server...")
    }
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, null, tint = color, modifier = Modifier.size(16.dp))
        Spacer(Modifier.size(6.dp))
        Text(label, style = MaterialTheme.typography.bodySmall, color = color)
    }
}

@Composable
private fun SettingsCard(apiUrl: String, onSave: (String) -> Unit, onTest: () -> Unit) {
    var url by remember(apiUrl) { mutableStateOf(apiUrl) }
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Server URL", fontWeight = FontWeight.Bold)
            Text(
                "Emulator: http://10.0.2.2:8000\nReal phone: http://YOUR_PC_IP:8000",
                style = MaterialTheme.typography.bodySmall,
            )
            OutlinedTextField(
                value = url,
                onValueChange = { url = it },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { onSave(url) }, modifier = Modifier.weight(1f)) { Text("Save") }
                OutlinedButton(onClick = onTest, modifier = Modifier.weight(1f)) { Text("Test") }
            }
        }
    }
}

@Composable
private fun SolutionCard(solution: SolveResponse) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(2.dp),
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            SectionTitle("Detected Problem")
            Text(solution.detectedProblem, fontFamily = FontFamily.Monospace)

            SectionTitle("Problem Type")
            Text(solution.problemType, fontWeight = FontWeight.SemiBold)

            SectionTitle("Solution")
            solution.steps.forEach { step ->
                Text(step.title, fontWeight = FontWeight.Bold)
                Text(step.content, fontFamily = FontFamily.Monospace, style = MaterialTheme.typography.bodyMedium)
                Spacer(Modifier.height(4.dp))
            }

            if (solution.solutions.isNotEmpty()) {
                SectionTitle("Answers")
                solution.solutions.forEach { Text("• $it", fontFamily = FontFamily.Monospace) }
            }

            SectionTitle("Verification")
            val verifiedColor = if (solution.verified) Success else Error
            Text(
                if (solution.verified) "✓ Verified" else "Could not verify",
                color = verifiedColor,
                fontWeight = FontWeight.Bold,
            )
            if (solution.verificationDetail.isNotBlank()) {
                Text(solution.verificationDetail, style = MaterialTheme.typography.bodySmall)
            }

            if (solution.explanation.isNotBlank()) {
                SectionTitle("Explanation")
                Text(solution.explanation.replace("**", ""))
            }
        }
    }
}

@Composable
private fun SectionTitle(text: String) {
    Text(text, style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.primary)
}
