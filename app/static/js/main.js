/**
 * 자산관리 시스템 메인 JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // 사이드바 토글
    setupSidebarToggle();
    
    // 현재 페이지 메뉴 활성화
    activateCurrentMenu();
    
    // 툴팁 초기화 (Bootstrap)
    initTooltips();
});

/**
 * 사이드바 토글 설정
 */
function setupSidebarToggle() {
    const mobileToggle = document.getElementById('mobile-toggle');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            document.querySelector('.app-container').classList.toggle('sidebar-mobile-open');
        });
    }
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.app-container').classList.toggle('sidebar-mobile-open');
        });
    }
    
    // 메인 콘텐츠 영역 클릭 시 모바일에서 사이드바 닫기
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.addEventListener('click', function(e) {
            if (window.innerWidth < 768 && document.querySelector('.app-container').classList.contains('sidebar-mobile-open')) {
                document.querySelector('.app-container').classList.remove('sidebar-mobile-open');
            }
        });
    }
}

/**
 * 현재 페이지에 해당하는 메뉴 활성화
 */
function activateCurrentMenu() {
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.sidebar-menu-link');
    
    // 정확한 경로 일치 여부를 확인하기 위한 변수
    let exactMatchFound = false;
    
    // 먼저 정확히 일치하는 경로가 있는지 확인
    menuLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath === href) {
            link.classList.add('active');
            const menuItem = link.closest('.sidebar-menu-item');
            if (menuItem) {
                menuItem.classList.add('active');
            }
            exactMatchFound = true;
        }
    });
    
    // 정확히 일치하는 항목이 없는 경우에만 시작 경로 확인
    if (!exactMatchFound) {
        menuLinks.forEach(link => {
            const href = link.getAttribute('href');
            // 루트 경로('/')가 아니고, 현재 경로가 href로 시작하는 경우
            if (href && href !== '/' && currentPath.startsWith(href + '/')) {
                link.classList.add('active');
                const menuItem = link.closest('.sidebar-menu-item');
                if (menuItem) {
                    menuItem.classList.add('active');
                }
            }
        });
    }
}

/**
 * Bootstrap 툴팁 초기화
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * 전역 알림 표시
 * @param {string} message - 표시할 메시지
 * @param {string} type - 알림 유형 (success, danger, warning, info)
 * @param {number} duration - 표시 시간 (밀리초)
 */
function showNotification(message, type = 'info', duration = 3000) {
    // 기존 알림 컨테이너 확인
    let container = document.querySelector('.notification-container');
    
    // 컨테이너가 없으면 생성
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
    
    // 알림 요소 생성
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${getIconForType(type)}"></i>
        </div>
        <div class="notification-content">${message}</div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // 컨테이너에 추가
    container.appendChild(notification);
    
    // 닫기 버튼 이벤트
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', function() {
        removeNotification(notification);
    });
    
    // 자동 제거 타이머
    if (duration > 0) {
        setTimeout(function() {
            removeNotification(notification);
        }, duration);
    }
    
    // 표시 애니메이션
    setTimeout(function() {
        notification.classList.add('show');
    }, 10);
}

/**
 * 알림 유형에 따른 아이콘 반환
 */
function getIconForType(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'danger': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        case 'info': 
        default: return 'info-circle';
    }
}

/**
 * 알림 요소 제거
 */
function removeNotification(notification) {
    notification.classList.remove('show');
    notification.classList.add('hide');
    
    setTimeout(function() {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

/**
 * 확인 대화상자 표시
 * @param {string} message - 표시할 메시지
 * @param {function} onConfirm - 확인 시 콜백
 * @param {function} onCancel - 취소 시 콜백
 * @param {string} confirmText - 확인 버튼 텍스트
 * @param {string} cancelText - 취소 버튼 텍스트
 */
function confirmDialog(message, onConfirm, onCancel = null, confirmText = '확인', cancelText = '취소') {
    // 기존 대화상자 제거
    const existingDialog = document.querySelector('.confirm-dialog-backdrop');
    if (existingDialog) {
        document.body.removeChild(existingDialog);
    }
    
    // 대화상자 요소 생성
    const backdrop = document.createElement('div');
    backdrop.className = 'confirm-dialog-backdrop';
    
    const dialog = document.createElement('div');
    dialog.className = 'confirm-dialog';
    dialog.innerHTML = `
        <div class="confirm-dialog-content">
            <div class="confirm-dialog-message">${message}</div>
            <div class="confirm-dialog-actions">
                <button class="btn btn-outline-secondary btn-sm confirm-dialog-cancel">${cancelText}</button>
                <button class="btn btn-primary btn-sm confirm-dialog-confirm">${confirmText}</button>
            </div>
        </div>
    `;
    
    backdrop.appendChild(dialog);
    document.body.appendChild(backdrop);
    
    // 애니메이션
    setTimeout(function() {
        backdrop.classList.add('show');
        dialog.classList.add('show');
    }, 10);
    
    // 이벤트 핸들러
    const confirmButton = dialog.querySelector('.confirm-dialog-confirm');
    const cancelButton = dialog.querySelector('.confirm-dialog-cancel');
    
    confirmButton.addEventListener('click', function() {
        closeDialog();
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    });
    
    cancelButton.addEventListener('click', function() {
        closeDialog();
        if (typeof onCancel === 'function') {
            onCancel();
        }
    });
    
    backdrop.addEventListener('click', function(e) {
        if (e.target === backdrop) {
            closeDialog();
            if (typeof onCancel === 'function') {
                onCancel();
            }
        }
    });
    
    // 대화상자 닫기 함수
    function closeDialog() {
        backdrop.classList.remove('show');
        dialog.classList.remove('show');
        
        setTimeout(function() {
            document.body.removeChild(backdrop);
        }, 300);
    }
}

/**
 * 날짜를 한국어 형식으로 포맷
 * @param {string} dateString - ISO 형식의 날짜 문자열
 * @returns {string} 포맷된 날짜 문자열
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * 문자열 길이 제한 함수
 * @param {string} str - 원본 문자열
 * @param {number} maxLength - 최대 길이
 * @returns {string} 제한된 문자열
 */
function limitString(str, maxLength) {
    if (!str) return '';
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

/**
 * 폼 데이터를 객체로 변환
 * @param {HTMLFormElement} form - 폼 요소
 * @returns {Object} 폼 데이터 객체
 */
function formToObject(form) {
    const formData = new FormData(form);
    const obj = {};
    
    for (let [key, value] of formData.entries()) {
        obj[key] = value;
    }
    
    return obj;
}

/**
 * 자산 위치 이미지에 마커 표시
 * @param {HTMLElement} container - 마커를 표시할 컨테이너
 * @param {Array} assets - 자산 데이터 배열
 */
function renderAssetMarkers(container, assets) {
    container.innerHTML = '';
    
    assets.forEach(asset => {
        if (asset.x_coordinate && asset.y_coordinate) {
            const marker = document.createElement('div');
            marker.className = 'asset-marker';
            marker.style.left = `${asset.x_coordinate}%`;
            marker.style.top = `${asset.y_coordinate}%`;
            marker.setAttribute('data-asset-id', asset.id);
            marker.setAttribute('data-asset-name', asset.name);
            marker.setAttribute('data-bs-toggle', 'tooltip');
            marker.setAttribute('data-bs-title', `${asset.name} (${asset.serial_number})`);
            
            container.appendChild(marker);
        }
    });
    
    // 툴팁 초기화
    initTooltips();
} 