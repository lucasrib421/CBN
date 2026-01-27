//Aqui irei traduzir os dados json que o docker manda para o typescript ler, 
// a estrutura de dados que vao ser traduzidos foi criada no:
//  C:\Users\gabri\OneDrive\Documentos\VisualStudioCodigos\CBN\homeNews\serializers.py 


// --- Blocos Básicos ---

export interface Media{
    id: number;
    title: string;
    file: string;
    alt_text?: string; // o "?" quer dizer que podemos receber ele vazio
    image_type: string;

}

export interface Author{
    id: number;
    name: string;
    bio?: string;
    avatar?: Media; // usamos a interface criada anteriomente 
}

export interface Category{
    id: number;
    name: string;
    slug: string; // O Slug pega o título, remove acentos, troca espaços por traços (-) e deixa tudo minúsculo
    color?: String; // recebe em hexadecimal 
}

export interface Tag{
    id: number;
    name: string;
    slug: string;
}

// --- Notícias ---