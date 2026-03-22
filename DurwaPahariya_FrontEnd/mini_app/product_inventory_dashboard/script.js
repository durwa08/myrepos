//Adding Products Data
let products = [
    { id: 1, name: "Laptop", price: 55000, stock: 5, category: "electronics" },
    { id: 2, name: "Phone", price: 20000, stock: 3, category: "electronics" },
    { id: 3, name: "Charger", price: 800, stock: 10, category: "electronics" },
    { id: 4, name: "Co-ord sets", price: 1800, stock: 2, category: "clothing" },
    { id: 5, name: "Tops and Shirts", price: 2000, stock: 2, category: "clothing" },
    { id: 6, name: "Jeans", price: 2500, stock: 2, category: "clothing" },
    { id: 7, name: "Story Books", price: 500, stock: 1, category: "books" },
    { id: 8, name: "Subject Books", price: 700, stock: 0, category: "books" },
    { id: 9, name: "Watch", price: 3000, stock: 4, category: "accessories" },
    { id: 10, name: "Bag", price: 1500, stock: 6, category: "accessories" },
    { id: 11, name: "Bracelets", price: 300, stock: 4, category: "accessories" },
    { id: 12, name: "Shoes", price: 3000, stock: 9, category: "accessories" }
    

];

// Trying to shows loading first
function gettingProducts() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(products);
        }, 1500);
    });
}

function displayProducts(data) {
    let loading = document.getElementById("loading");

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

    updateAnalytics(data);
}

// I combined all filtering logic in one place instead of scattering it
function handleFilters() {

    let searchVal= document.getElementById("search").value.toLowerCase();
    let category =document.getElementById("categoryFilter").value;
    let sort = document.getElementById("sort").value;

    let filtered= products.filter(p => {
        let matchSearch = p.name.toLowerCase().includes(searchVal);
        let matchCategory = category === "all" || p.category === category;
        return matchSearch && matchCategory;
    });

    // Sorting logic
    if (sort === "low") filtered.sort((a,b)=>a.price-b.price);
    if (sort === "high") filtered.sort((a,b)=>b.price-a.price);
    if (sort === "az") filtered.sort((a,b)=>a.name.localeCompare(b.name));
    if (sort === "za") filtered.sort((a,b)=>b.name.localeCompare(a.name));

    displayProducts(filtered);
}
// These values update every time product list changes
function updateAnalytics() {

    document.getElementById("total").innerText = products.length;

    let totalValue = products.reduce((sum, p) => sum + p.price * p.stock, 0);
    document.getElementById("value").innerText = totalValue;

    let out = products.filter(p => p.stock === 0).length;
    document.getElementById("out").innerText = out;
}

function deleteProduct(id) {

    // Removing product by filtering out matching id
    products = products.filter(p => p.id !== id);

    localStorage.setItem("products", JSON.stringify(products));

    handleFilters();
}

document.getElementById("form").addEventListener("submit", function(e) {

    e.preventDefault();

    let name = document.getElementById("name").value;
    let price = +document.getElementById("price").value;
    let stock = +document.getElementById("stock").value;
    let category = document.getElementById("category").value;

    // Basic validation so wrong data doesn’t enter system
    if (!name || price <= 0 || stock < 0 || !category) {
        alert("Please fill valid details");
        return;
    }

    let newProduct = {
        id: Date.now(), // quick unique id
        name,
        price,
        stock,
        category
    };

    products.push(newProduct);

    localStorage.setItem("products", JSON.stringify(products));

    handleFilters();

    this.reset(); // clearing form after submission
});

//Adding EvenListeners -they are used to detect user actions and run some codes when the action is triggered
document.getElementById("search").addEventListener("input", handleFilters);
document.getElementById("categoryFilter").addEventListener("change", handleFilters);
document.getElementById("sort").addEventListener("change", handleFilters);

// Showing loading first, then displaying data
document.addEventListener("DOMContentLoaded", async () => {

    let loading = document.getElementById("loading");
    let data = await gettingProducts();
    displayProducts(data);
    loading.style.display = "none";

    
});