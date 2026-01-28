import { BrowserRouter } from 'react-router-dom';
import { AppRoutes } from './routes';
import { Header } from './components/Header';
function App() {
  return (

    <div className='App'>
      <Header></Header>

      <main style={{ padding: '20px' }}>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </main>
      
    </div> 

  );
}

export default App;