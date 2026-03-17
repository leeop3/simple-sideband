// BluetoothService.kt - Classic Bluetooth (RFCOMM/SPP) for RNode
package org.simplesideband.simplesideband

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothSocket
import android.content.Context
import android.util.Log
import org.kivy.android.PythonActivity
import java.io.BufferedInputStream
import java.io.OutputStream
import java.util.UUID

class BluetoothService private constructor(private val context: Context) {
    
    companion object {
        private const val TAG = "BluetoothService"
        private const val SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"
        
        @Volatile private var instance: BluetoothService? = null
        
        fun getInstance(activity: PythonActivity): BluetoothService {
            if (instance == null) {
                synchronized(this) {
                    if (instance == null) {
                        instance = BluetoothService(activity.applicationContext)
                    }
                }
            }
            return instance!!
        }
    }
    
    @Volatile private var bluetoothSocket: BluetoothSocket? = null
    @Volatile private var bufferedInput: BufferedInputStream? = null
    @Volatile private var outputStream: OutputStream? = null
    @Volatile private var deviceAddress: String? = null
    @Volatile private var isConnected = false
    
    private val bluetoothAdapter: BluetoothAdapter by lazy {
        BluetoothAdapter.getDefaultAdapter()
    }
    
    suspend fun connect(deviceAddress: String): Boolean {
        this.deviceAddress = deviceAddress
        return connectInternal(deviceAddress)
    }
    
    private fun connectInternal(address: String): Boolean {
        return try {
            try { bluetoothSocket?.close() } catch (_: Exception) {}
            
            Log.i(TAG, "Connecting to RNode at $address...")
            
            val device = bluetoothAdapter.getRemoteDevice(address)
            val uuid = UUID.fromString(SPP_UUID)
            
            // Create RFCOMM socket (Classic Bluetooth, NOT BLE)
            bluetoothSocket = device.createRfcommSocketToServiceRecord(uuid)
            bluetoothAdapter.cancelDiscovery()
            bluetoothSocket?.connect()
            
            bufferedInput = BufferedInputStream(bluetoothSocket?.inputStream, 4096)
            outputStream = bluetoothSocket?.outputStream
            
            isConnected = true
            Log.i(TAG, "RNode connected via RFCOMM/SPP")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "Connection failed: ${e.message}")
            disconnect()
            false
        }
    }
    
    fun read(maxBytes: Int): ByteArray {
        return try {
            if (!isConnected || bufferedInput == null) {
                return ByteArray(0)
            }
            
            val available = bufferedInput?.available() ?: 0
            if (available > 0) {
                val toRead = minOf(available, maxBytes)
                val buffer = ByteArray(toRead)
                val bytesRead = bufferedInput?.read(buffer, 0, toRead) ?: 0
                if (bytesRead > 0) {
                    buffer.copyOf(bytesRead)
                } else {
                    ByteArray(0)
                }
            } else {
                ByteArray(0)
            }
        } catch (e: Exception) {
            Log.w(TAG, "Read error: ${e.message}")
            isConnected = false
            ByteArray(0)
        }
    }
    
    fun write(data: ByteArray) {
        if (!isConnected || outputStream == null) {
            return
        }
        
        try {
            outputStream?.write(data)
            outputStream?.flush()
        } catch (e: Exception) {
            Log.w(TAG, "Write error: ${e.message}")
            isConnected = false
        }
    }
    
    fun disconnect() {
        try { bufferedInput?.close() } catch (_: Exception) {}
        try { outputStream?.close() } catch (_: Exception) {}
        try { bluetoothSocket?.close() } catch (_: Exception) {}
        
        bluetoothSocket = null
        bufferedInput = null
        outputStream = null
        isConnected = false
        
        Log.i(TAG, "Disconnected from RNode")
    }
    
    fun isConnected(): Boolean = isConnected
    fun getDeviceAddress(): String? = deviceAddress
}