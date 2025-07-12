/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly REACT_APP_API_URL: string;
  readonly REACT_APP_WS_URL: string;
  readonly REACT_APP_ENV: string;
  readonly REACT_APP_VERSION: string;
  readonly REACT_APP_APP_NAME: string;
  readonly REACT_APP_DEBUG: string;
  readonly REACT_APP_TIMEOUT: string;
  readonly REACT_APP_UPLOAD_URL: string;
  readonly REACT_APP_WEBSOCKET_URL: string;
  readonly REACT_APP_GRAPHQL_URL: string;
  readonly REACT_APP_BLOCKCHAIN_URL: string;
  readonly REACT_APP_METAVERSE_URL: string;
  readonly REACT_APP_AI_URL: string;
  readonly REACT_APP_SEARCH_URL: string;
  readonly REACT_APP_QUANTUM_URL: string;
  readonly REACT_APP_FEDERATED_URL: string;
  readonly REACT_APP_MOBILE_URL: string;
  // 更多环境变量...
  readonly [key: string]: string | undefined;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 