/**
 * appStore.js – lightweight global state using React Context + useReducer.
 * Wrap your app with <AppProvider> and consume with useAppStore().
 */
import { createContext, useContext, useReducer } from 'react';

const initialState = {
  diseaseResult: null,
  yieldResult: null,
  marketResult: null,
  loading: { disease: false, yield: false, market: false },
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_DISEASE':  return { ...state, diseaseResult: action.payload };
    case 'SET_YIELD':    return { ...state, yieldResult:   action.payload };
    case 'SET_MARKET':   return { ...state, marketResult:  action.payload };
    case 'SET_LOADING':  return { ...state, loading: { ...state.loading, ...action.payload } };
    default: return state;
  }
}

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>;
}

export function useAppStore() {
  return useContext(AppContext);
}
