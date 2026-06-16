// Crypto Market Tracker - Frontend JavaScript

let currentPage = 1;
let totalPages = 1;
let currentFilters = {};

// Load global stats on page load
$(document).ready(function() {
    loadGlobalStats();
    loadMarketData();
    
    // Event listeners
    $('#applyFilters').click(function() {
        currentPage = 1;
        loadMarketData();
    });
    
    $('#searchInput').on('keypress', function(e) {
        if (e.which === 13) {
            currentPage = 1;
            loadMarketData();
        }
    });
});

function loadGlobalStats() {
    $.ajax({
        url: '/api/global',
        method: 'GET',
        success: function(response) {
            if (response.success && response.data) {
                const data = response.data;
                $('#totalMarketCap').text(formatNumber(data.total_market_cap?.usd || 0, 'USD'));
                $('#totalVolume').text(formatNumber(data.total_volume?.usd || 0, 'USD'));
                $('#btcDominance').text((data.market_cap_percentage?.btc || 0).toFixed(1) + '%');
                $('#activeCoins').text(data.active_cryptocurrencies?.toLocaleString() || 'N/A');
            }
        },
        error: function() {
            console.error('Failed to load global stats');
            $('#totalMarketCap').text('Error');
        }
    });
}

function loadMarketData() {
    showLoading(true);
    
    // Build query parameters
    const params = {
        page: currentPage,
        per_page: $('#perPage').val(),
        search: $('#searchInput').val(),
        price_range: $('#priceRange').val(),
        cap_category: $('#capCategory').val(),
        volume_category: $('#volumeCategory').val(),
        performance: $('#performance').val(),
        sort_by: $('#sortBy').val(),
        sort_order: $('#sortOrder').val()
    };
    
    currentFilters = params;
    
    $.ajax({
        url: '/api/markets',
        method: 'GET',
        data: params,
        success: function(response) {
            if (response.success) {
                renderTable(response.data);
                totalPages = response.total_pages;
                renderPagination(response.page, response.total_pages);
            } else {
                $('#tableBody').html('<tr><td colspan="8" class="text-center text-danger">Error: ' + (response.error || 'Unknown error') + '</td></tr>');
            }
            showLoading(false);
        },
        error: function(xhr) {
            console.error('API Error:', xhr);
            $('#tableBody').html('<tr><td colspan="8" class="text-center text-danger">Failed to load market data. Please try again.</td></tr>');
            showLoading(false);
        }
    });
}

function renderTable(coins) {
    if (!coins || coins.length === 0) {
        $('#tableBody').html('<tr><td colspan="8" class="text-center">No coins found matching criteria</td></tr>');
        return;
    }
    
    let html = '';
    coins.forEach((coin, index) => {
        const changeClass = coin.price_change_percentage_24h >= 0 ? 'positive-change' : 'negative-change';
        const changeIcon = coin.price_change_percentage_24h >= 0 ? '▲' : '▼';
        const changeValue = Math.abs(coin.price_change_percentage_24h).toFixed(2);
        
        html += `
            <tr>
                <td>${(currentPage - 1) * currentFilters.per_page + index + 1}</td>
                <td>
                    <img src="${coin.image_url}" alt="${coin.name}" class="coin-image" onerror="this.src='https://via.placeholder.com/32'">
                    ${coin.name}
                </td>
                <td><strong>${coin.symbol}</strong></td>
                <td>${formatPrice(coin.current_price)}</td>
                <td class="${changeClass}">${changeIcon} ${changeValue}%</td>
                <td>${formatNumber(coin.market_cap, 'USD')}</td>
                <td>${formatNumber(coin.total_volume, 'USD')}</td>
                <td>#${coin.market_cap_rank}</td>
            </tr>
        `;
    });
    
    $('#tableBody').html(html);
}

function renderPagination(currentPage, totalPages) {
    if (totalPages <= 1) {
        $('#pagination').empty();
        return;
    }
    
    let html = '';
    
    // Previous button
    if (currentPage > 1) {
        html += `<li class="page-item"><a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a></li>`;
    } else {
        html += `<li class="page-item disabled"><span class="page-link">Previous</span></li>`;
    }
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
        } else {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
    }
    
    // Next button
    if (currentPage < totalPages) {
        html += `<li class="page-item"><a class="page-link" href="#" data-page="${currentPage + 1}">Next</a></li>`;
    } else {
        html += `<li class="page-item disabled"><span class="page-link">Next</span></li>`;
    }
    
    $('#pagination').html(html);
    
    // Attach click handlers
    $('.page-link[data-page]').click(function(e) {
        e.preventDefault();
        currentPage = parseInt($(this).data('page'));
        loadMarketData();
    });
}

function showLoading(show) {
    if (show) {
        $('#loadingSpinner').show();
        $('#cryptoTable').hide();
    } else {
        $('#loadingSpinner').hide();
        $('#cryptoTable').show();
    }
}

function formatNumber(num, currency = null) {
    if (!num || num === 0) return currency ? '$0' : '0';
    
    if (num >= 1e12) {
        return (currency ? '$' : '') + (num / 1e12).toFixed(2) + 'T';
    } else if (num >= 1e9) {
        return (currency ? '$' : '') + (num / 1e9).toFixed(2) + 'B';
    } else if (num >= 1e6) {
        return (currency ? '$' : '') + (num / 1e6).toFixed(2) + 'M';
    } else {
        return (currency ? '$' : '') + num.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
}

function formatPrice(price) {
    if (price < 0.01) {
        return '$' + price.toFixed(8);
    } else if (price < 1) {
        return '$' + price.toFixed(4);
    } else {
        return '$' + price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
}