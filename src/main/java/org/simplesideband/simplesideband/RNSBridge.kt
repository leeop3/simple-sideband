// RNSBridge.kt - Bridge Kotlin Bluetooth to Python RNS
package org.simplesideband.simplesideband

import android.util.Log
import org.kivy.android.PythonActivity

object RNSBridge {
    private const val TAG = "RNSBridge"
    
    @Volatile private var btService: BluetoothService? = null
    @Volatile private var isInitialized = false
    
    fun initialize(pythonActivity: PythonActivity): Boolean {
        return try {
            Log.i(TAG, "Initializing RNSBridge...")
            btService = BluetoothService.getInstance(pythonActivity)
            isInitialized = true
            Log.i(TAG, "RNSBridge initialized")
            true
        } catch (e: Exception) {
            Log.e(TAG, "RNSBridge init failed: ${e.message}")
            false
        }
    }
    
    fun connectRNode(deviceAddress: String): Boolean {
        if (!isInitialized || btService == null) {
            Log.e(TAG, "RNSBridge not initialized")
            return false
        }
        
        return try {
            Log.i(TAG, "Connecting to RNode at $deviceAddress...")
            val success = btService?.connect(deviceAddress) ?: false
            if (success) {
                Log.i(TAG, "RNode connected")
            } else {
                Log.e(TAG, "RNode connection failed")
            }
            success
        } catch (e: Exception) {
            Log.e(TAG, "RNode connect error: ${e.message}")
            false
        }
    }
    
    fun disconnectRNode() {
        try {
            btService?.disconnect()
            Log.i(TAG, "RNode disconnected")
        } catch (e: Exception) {
            Log.e(TAG, "Disconnect error: ${e.message}")
        }
    }
    
    fun isConnected(): Boolean = btService?.isConnected() ?: false
    
    fun readData(maxBytes: Int): ByteArray {
        return try {
            btService?.read(maxBytes) ?: ByteArray(0)
        } catch (e: Exception) {
            Log.w(TAG, "Read error: ${e.message}")
            ByteArray(0)
        }
    }
    
    fun writeData(data: ByteArray) {
        try {
            btService?.write(data)
        } catch (e: Exception) {
            Log.w(TAG, "Write error: ${e.message}")
        }
    }
}