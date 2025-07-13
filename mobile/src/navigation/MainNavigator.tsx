import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// 主屏幕组件
const HomeScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>智能思维</Text>
    <Text style={styles.subtitle}>AI驱动的3D思维空间</Text>
  </View>
);

// 思维分析屏幕
const ThinkingScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>思维分析</Text>
    <Text style={styles.subtitle}>探索您的思维模式</Text>
  </View>
);

// 协作屏幕
const CollaborationScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>协作空间</Text>
    <Text style={styles.subtitle}>与他人共享思维</Text>
  </View>
);

// 3D空间屏幕
const ThreeDScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>3D思维空间</Text>
    <Text style={styles.subtitle}>沉浸式思维体验</Text>
  </View>
);

// 设置屏幕
const SettingsScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>设置</Text>
    <Text style={styles.subtitle}>个性化您的体验</Text>
  </View>
);

// 底部标签导航器
const TabNavigator = () => (
  <Tab.Navigator
    screenOptions={{
      tabBarActiveTintColor: '#6200ea',
      tabBarInactiveTintColor: '#999',
      headerShown: false,
    }}
  >
    <Tab.Screen
      name="Home"
      component={HomeScreen}
      options={{
        tabBarLabel: '首页',
      }}
    />
    <Tab.Screen
      name="Thinking"
      component={ThinkingScreen}
      options={{
        tabBarLabel: '思维',
      }}
    />
    <Tab.Screen
      name="ThreeD"
      component={ThreeDScreen}
      options={{
        tabBarLabel: '3D',
      }}
    />
    <Tab.Screen
      name="Collaboration"
      component={CollaborationScreen}
      options={{
        tabBarLabel: '协作',
      }}
    />
    <Tab.Screen
      name="Settings"
      component={SettingsScreen}
      options={{
        tabBarLabel: '设置',
      }}
    />
  </Tab.Navigator>
);

// 主导航器
export const MainNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="Main" component={TabNavigator} />
    </Stack.Navigator>
  );
};

// 样式定义
const styles = StyleSheet.create({
  screen: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
}); 