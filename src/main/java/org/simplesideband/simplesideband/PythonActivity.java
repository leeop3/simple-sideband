// PythonActivity.java - With Bluetooth Service Integration
// Package MUST match your app: org.yourname.simplesideband

package org.simplesideband.simplesideband;

import android.os.Bundle;
import android.util.Log;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.content.Context;
import android.content.pm.PackageManager;

import org.kivy.android.PythonActivity;
import org.kivy.android.PythonService;

public class PythonActivity extends PythonActivity {
    
    private static final String TAG = "PythonActivity";
    private static PythonActivity instance = null;
    private BluetoothService bluetoothService = null;
    private RNSBridge rnsBridge = null;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.i(TAG, "PythonActivity onCreate - Initializing Bluetooth...");
        super.onCreate(savedInstanceState);
        instance = this;
        
        // Initialize Bluetooth Service
        try {
            bluetoothService = BluetoothService.getInstance(this);
            Log.i(TAG, "✅ BluetoothService initialized");
        } catch (Exception e) {
            Log.e(TAG, "❌ BluetoothService init failed: " + e.getMessage());
        }
        
        // Initialize RNS Bridge
        try {
            rnsBridge = new RNSBridge();
            rnsBridge.initialize(this);
            Log.i(TAG, "✅ RNSBridge initialized");
        } catch (Exception e) {
            Log.e(TAG, "❌ RNSBridge init failed: " + e.getMessage());
        }
        
        // Check Bluetooth availability
        checkBluetoothAvailability();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        Log.i(TAG, "PythonActivity onResume");
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        Log.i(TAG, "PythonActivity onPause");
    }
    
    @Override
    protected void onDestroy() {
        Log.i(TAG, "PythonActivity onDestroy - Cleaning up Bluetooth...");
        
        // Clean up Bluetooth connections
        if (bluetoothService != null) {
            try {
                bluetoothService.disconnect();
                Log.i(TAG, "BluetoothService disconnected");
            } catch (Exception e) {
                Log.e(TAG, "BluetoothService cleanup error: " + e.getMessage());
            }
        }
        
        instance = null;
        super.onDestroy();
    }
    
    // Check if Bluetooth is available on this device
    private void checkBluetoothAvailability() {
        BluetoothManager bm = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        if (bm == null) {
            Log.w(TAG, "⚠️ BluetoothManager not available");
            return;
        }
        
        BluetoothAdapter ba = bm.getAdapter();
        if (ba == null) {
            Log.w(TAG, "⚠️ BluetoothAdapter not available");
            return;
        }
        
        if (!ba.isEnabled()) {
            Log.w(TAG, "⚠️ Bluetooth is disabled");
        } else {
            Log.i(TAG, "✅ Bluetooth is enabled: " + ba.getAddress());
        }
        
        // Check for required permissions
        if (checkSelfPermission(android.Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            Log.w(TAG, "⚠️ BLUETOOTH_CONNECT permission not granted");
        } else {
            Log.i(TAG, "✅ BLUETOOTH_CONNECT permission granted");
        }
    }
    
    // Get PythonActivity instance (for Kotlin to access)
    public static PythonActivity getInstance() {
        return instance;
    }
    
    // Get BluetoothService instance (for Python to access via PyJNIus)
    public BluetoothService getBluetoothService() {
        return bluetoothService;
    }
    
    // Get RNSBridge instance (for Python to access via PyJNIus)
    public RNSBridge getRNSBridge() {
        return rnsBridge;
    }
    
    // Connect to RNode (called from Python via PyJNIus)
    public boolean connectRNode(String deviceAddress) {
        if (bluetoothService == null) {
            Log.e(TAG, "❌ BluetoothService not initialized");
            return false;
        }
        
        try {
            Log.i(TAG, "Connecting to RNode at " + deviceAddress);
            boolean success = bluetoothService.connect(deviceAddress);
            if (success) {
                Log.i(TAG, "✅ RNode connected");
            } else {
                Log.e(TAG, "❌ RNode connection failed");
            }
            return success;
        } catch (Exception e) {
            Log.e(TAG, "❌ Connect error: " + e.getMessage());
            return false;
        }
    }
    
    // Disconnect from RNode (called from Python via PyJNIus)
    public void disconnectRNode() {
        if (bluetoothService != null) {
            bluetoothService.disconnect();
            Log.i(TAG, "RNode disconnected");
        }
    }
    
    // Check connection status (called from Python via PyJNIus)
    public boolean isRNodeConnected() {
        return bluetoothService != null && bluetoothService.isConnected();
    }
}