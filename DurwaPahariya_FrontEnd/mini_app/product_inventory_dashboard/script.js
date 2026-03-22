//Adding Products Data
let products = [
    { id: 1, name: "Laptop", price: 55000, stock: 5, category: "electronics" },
    { id: 2, name: "Phone", price: 20000, stock: 3, category: "electronics" },
    { id: 3, name: "Charger", price: 800, stock: 10, category: "electronics" },
    { id: 4, name: "Co-ord sets", price: 1800, stock: 2, category: "clothing" },
    { id: 5, name: "Tops and Shirts", price: 2000, stock: 2, category: "clothing" },
    { id: 4, name: "Jeans", price: 2500, stock: 2, category: "clothing" },
    { id: 7, name: "Story Books", price: 500, stock: 1, category: "books" },
    { id: 8, name: "Subject Books", price: 700, stock: 0, category: "books" },
    { id: 9, name: "Watch", price: 3000, stock: 4, category: "accessories" },
    { id: 10, name: "Bag", price: 1500, stock: 6, category: "accessories" },
    { id: 11, name: "Bracelets", price: 300, stock: 4, category: "accessories" },
    { id: 9, name: "Shoes", price: 3000, stock: 9, category: "accessories" }
    

];

// Trying to shows loading first
function fetchProducts() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(products);
        }, 1500);
    });
}

function renderProducts(data) {

    let container = document.getElementById("productContainer");
    container.innerHTML = "";

    // If nothing matches filters, show message instead of blank screen like no poduct found
    if (data.length === 0) {
        container.innerHTML = "<p>No products found 😢</p>";
        return;
    }

    data.forEach(p => {

        // Simple stock color logic so that user can quickly identify
        let color = p.stock === 0 ? "red" : p.stock < 5 ? "orange" : "green";

        let div = document.createElement("div");
        div.className = "card";

        div.innerHTML = `
            <h3>${p.name}</h3>
            <p>${p.category}</p>
            <p>₹${p.price}</p>
            <p style="color:${color}">Stock: ${p.stock}</p>
            <button onclick="deleteProduct(${p.id})">Delete</button>
        `;

        container.appendChild(div);
    });

    updateAnalytics();
}