import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Image,
  Dimensions,
} from 'react-native';
import { Mic } from 'react-native-vector-icons/FontAwesome';
import Voice from '@react-native-voice/voice';
import axios from 'axios';

const { width } = Dimensions.get('window');

const RobotControlScreen = () => {
  const [command, setCommand] = useState('');
  const [status, setStatus] = useState('Ready');
  const [position, setPosition] = useState({ x: 0, y: 0, facing: 0 });
  const [isListening, setIsListening] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [history, setHistory] = useState([]);
  const [robotMode, setRobotMode] = useState('simulator');
  const [confidence, setConfidence] = useState(0);
  const [botType, setBotType] = useState('whatsapp'); // 'whatsapp', 'telegram', 'api'
  const [phoneNumber, setPhoneNumber] = useState('');
  const [telegramChatId, setTelegramChatId] = useState('');
  const [apiUrl, setApiUrl] = useState('http://localhost:5000');
  const [learningData, setLearningData] = useState(null);

  const API_BASE_URL = apiUrl;

  useEffect(() => {
    Voice.onSpeechStart = onSpeechStart;
    Voice.onSpeechRecognized = onSpeechRecognized;
    Voice.onSpeechEnd = onSpeechEnd;
    Voice.onSpeechError = onSpeechError;
    Voice.onSpeechResults = onSpeechResults;
    Voice.onSpeechPartialResults = onSpeechPartialResults;

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  const onSpeechStart = () => setIsListening(true);
  const onSpeechRecognized = () => { };
  const onSpeechEnd = () => setIsListening(false);
  const onSpeechError = (e) => {
    Alert.alert('Speech Error', e.error);
    setIsListening(false);
  };
  const onSpeechResults = (e) => {
    const text = e.value[0];
    setCommand(text);
  };
  const onSpeechPartialResults = (e) => {
    setCommand(e.value[0] || '');
  };

  const startListening = async () => {
    try {
      await Voice.start('en-US');
    } catch (e) {
      Alert.alert('Error', 'Could not start voice recognition');
    }
  };

  const stopListening = async () => {
    try {
      await Voice.stop();
    } catch (e) {
      Alert.alert('Error', 'Could not stop voice recognition');
    }
  };

  const executeCommand = async () => {
    if (!command.trim()) {
      Alert.alert('Error', 'Please enter a command');
      return;
    }

    setIsExecuting(true);
    try {
      // Parse command
      const parseResponse = await axios.post(`${API_BASE_URL}/api/parse`, {
        text: command,
      });

      const parsed = parseResponse.data;
      setConfidence(parsed.confidence || 0);

      // Execute command
      const executeResponse = await axios.post(`${API_BASE_URL}/api/execute`, {
        action: parsed.action,
        direction: parsed.direction,
        distance_cm: parsed.distance_cm,
        angle_deg: parsed.angle_deg,
      });

      // Update status
      setStatus(`✓ ${parsed.action}`);
      
      // Add to history
      setHistory([
        ...history.slice(0, 9),
        {
          command,
          action: parsed.action,
          success: true,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);

      // Fetch updated robot status
      const statusResponse = await axios.get(`${API_BASE_URL}/api/status`);
      setPosition({
        x: statusResponse.data.x,
        y: statusResponse.data.y,
        facing: statusResponse.data.facing,
      });

      setCommand('');
    } catch (error) {
      Alert.alert('Error', error.response?.data?.error || 'Command failed');
      setStatus('✗ Error');
    } finally {
      setIsExecuting(false);
    }
  };

  const fetchRobotStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/status`);
      setRobotMode(response.data.mode);
      setPosition({
        x: response.data.x,
        y: response.data.y,
        facing: response.data.facing,
      });
    } catch (error) {
      Alert.alert('Error', 'Could not fetch robot status');
    }
  };

  const fetchLearningData = async () => {
    try {
      // This would need a new endpoint on the backend
      const response = await axios.get(`${API_BASE_URL}/api/learning/report`);
      setLearningData(response.data);
    } catch (error) {
      console.log('Learning endpoint not available');
    }
  };

  useEffect(() => {
    const statusInterval = setInterval(fetchRobotStatus, 2000);
    return () => clearInterval(statusInterval);
  }, []);

  useEffect(() => {
    fetchLearningData();
  }, []);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🤖 OpenGuy Mobile</Text>
        <Text style={styles.subtitle}>Control Your Robot Anywhere</Text>
      </View>

      {/* Connection Config */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚙️ Configuration</Text>
        
        <View style={styles.subSection}>
          <Text style={styles.label}>API Endpoint:</Text>
          <TextInput
            style={styles.input}
            placeholder="http://localhost:5000"
            value={apiUrl}
            onChangeText={setApiUrl}
            placeholderTextColor="#999"
          />
        </View>

        <View style={styles.subSection}>
          <Text style={styles.label}>Control via:</Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity
              style={[
                styles.modeButton,
                botType === 'api' && styles.modeButtonActive,
              ]}
              onPress={() => setBotType('api')}
            >
              <Text style={styles.modeButtonText}>Direct API</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.modeButton,
                botType === 'whatsapp' && styles.modeButtonActive,
              ]}
              onPress={() => setBotType('whatsapp')}
            >
              <Text style={styles.modeButtonText}>WhatsApp</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.modeButton,
                botType === 'telegram' && styles.modeButtonActive,
              ]}
              onPress={() => setBotType('telegram')}
            >
              <Text style={styles.modeButtonText}>Telegram</Text>
            </TouchableOpacity>
          </View>
        </View>

        {botType === 'whatsapp' && (
          <TextInput
            style={styles.input}
            placeholder="Your WhatsApp number (+1234567890)"
            value={phoneNumber}
            onChangeText={setPhoneNumber}
            placeholderTextColor="#999"
            keyboardType="phone-pad"
          />
        )}

        {botType === 'telegram' && (
          <TextInput
            style={styles.input}
            placeholder="Your Telegram Chat ID"
            value={telegramChatId}
            onChangeText={setTelegramChatId}
            placeholderTextColor="#999"
            keyboardType="numeric"
          />
        )}
      </View>

      {/* Robot Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Status</Text>
        <View style={styles.statusBox}>
          <View style={styles.statusItem}>
            <Text style={styles.label}>Mode:</Text>
            <Text style={styles.statusValue}>
              {robotMode === 'hardware' ? '🟢 Hardware' : '🟡 Simulator'}
            </Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.label}>Position:</Text>
            <Text style={styles.statusValue}>
              ({position.x.toFixed(1)}, {position.y.toFixed(1)})
            </Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.label}>Facing:</Text>
            <Text style={styles.statusValue}>{position.facing.toFixed(0)}°</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.label}>Confidence:</Text>
            <Text style={styles.statusValue}>
              {(confidence * 100).toFixed(0)}%
            </Text>
          </View>
        </View>
      </View>

      {/* Learning Data */}
      {learningData && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🧠 Robot Learning</Text>
          <View style={styles.statusBox}>
            <View style={styles.statusItem}>
              <Text style={styles.label}>Success Rate:</Text>
              <Text style={styles.statusValue}>
                {learningData.overall_success_rate}
              </Text>
            </View>
            <View style={styles.statusItem}>
              <Text style={styles.label}>Learned Strategies:</Text>
              <Text style={styles.statusValue}>
                {learningData.learned_strategies}
              </Text>
            </View>
            <View style={styles.statusItem}>
              <Text style={styles.label}>Total Experiences:</Text>
              <Text style={styles.statusValue}>
                {learningData.total_experiences}
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* Command Input */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎤 Command</Text>
        <TextInput
          style={styles.commandInput}
          placeholder="Type a command or speak..."
          value={command}
          onChangeText={setCommand}
          placeholderTextColor="#999"
          editable={!isListening}
        />
        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, isListening && styles.buttonActive]}
            onPress={isListening ? stopListening : startListening}
            disabled={isExecuting}
          >
            <Text style={styles.buttonText}>
              {isListening ? '⏹️ Stop' : '🎤 Listen'}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.button, styles.buttonPrimary]}
            onPress={executeCommand}
            disabled={isExecuting}
          >
            {isExecuting ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>▶️ Execute</Text>
            )}
          </TouchableOpacity>
        </View>
        <View style={styles.statusBar}>
          <Text style={styles.statusText}>{status}</Text>
        </View>
      </View>

      {/* History */}
      {history.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📜 History</Text>
          {history.reverse().map((item, index) => (
            <View key={index} style={styles.historyItem}>
              <Text style={styles.historyCommand}>{item.command}</Text>
              <View style={styles.historyMeta}>
                <Text style={styles.historyAction}>{item.action}</Text>
                <Text style={styles.historyTime}>{item.timestamp}</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Quick Commands */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ Quick Commands</Text>
        <View style={styles.quickCommandGrid}>
          {[
            'move forward',
            'rotate right',
            'grab',
            'release',
            'move backward',
            'status',
          ].map((cmd) => (
            <TouchableOpacity
              key={cmd}
              style={styles.quickCommandButton}
              onPress={() => {
                setCommand(cmd);
              }}
            >
              <Text style={styles.quickCommandText}>{cmd}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 12,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
    paddingTop: 12,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  subSection: {
    marginBottom: 12,
  },
  label: {
    fontSize: 13,
    color: '#666',
    marginBottom: 6,
    fontWeight: '500',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 10,
    fontSize: 14,
    backgroundColor: '#f9f9f9',
    color: '#333',
  },
  commandInput: {
    borderWidth: 2,
    borderColor: '#4CAF50',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
    color: '#333',
    marginBottom: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonActive: {
    backgroundColor: '#ff6b6b',
  },
  buttonPrimary: {
    backgroundColor: '#4CAF50',
  },
  buttonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 8,
  },
  modeButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 6,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  modeButtonActive: {
    backgroundColor: '#4CAF50',
    borderColor: '#4CAF50',
  },
  modeButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
  },
  statusBox: {
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 12,
    gap: 8,
  },
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4CAF50',
  },
  statusBar: {
    backgroundColor: '#e8f5e9',
    borderRadius: 6,
    padding: 10,
    alignItems: 'center',
  },
  statusText: {
    fontSize: 14,
    color: '#2e7d32',
    fontWeight: '500',
  },
  historyItem: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  historyCommand: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  historyMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  historyAction: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '500',
  },
  historyTime: {
    fontSize: 12,
    color: '#999',
  },
  quickCommandGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  quickCommandButton: {
    width: (width - 48) / 2,
    paddingVertical: 10,
    borderRadius: 6,
    backgroundColor: '#4CAF50',
    alignItems: 'center',
  },
  quickCommandText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#fff',
  },
});

export default RobotControlScreen;
