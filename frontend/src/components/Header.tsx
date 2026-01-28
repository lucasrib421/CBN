import { useState, useEffect } from 'react'; 
import { NewsService } from '../services/newsService';
import type { Menu } from '../types'; // Nosso tipo

export const Header = () => {
const [menuData, setMenuData] = useState<Menu | null>(null);

useEffect(()=>{
    const fetchMenu = async () => {
      try {
        const menus = await NewsService.getMenus();
        
        console.log("O que veio da API:", menus); // Dica: Olhe o Console do navegador (F12)

        if (menus.length > 0) {
          setMenuData(menus[0]); 
        }
      } catch (error) {
        console.error("Deu erro ao buscar:", error);
      }
    };

    // Executamos a função imediatamente
    fetchMenu();
},[]);


  return (
    <header style={{ padding: '1rem', background: '#222', color: 'white' }}>
      <h1>CBN - Clone</h1>
      <p>{menuData ? "Menu Carregado!" : "Carregando dados..."}</p>
    </header>
  );
};