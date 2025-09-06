function applyTopPadding() {
    // Update various absolute positions to match where the main container
    // starts. This is necessary for handling multi-line nav headers, since
    // that pushes the main container down.
    var container = document.querySelector('body > [class*="container"]');
    if (!container) return; // Exit early if no container found
    var offset = container.offsetTop;

    document.documentElement.style.scrollPaddingTop = offset + 'px';
    document.querySelectorAll('.bs-sidebar.affix').forEach(function (sidebar) {
        sidebar.style.top = offset + 'px';
    });
}

window.addEventListener('resize', applyTopPadding);

var scrollSpy = new bootstrap.ScrollSpy(document.body, {
    target: '.bs-sidebar'
});

/* Prevent disabled links from causing a page reload */
document.querySelectorAll("li.disabled a").forEach(function (item) {
    item.addEventListener("click", function (event) {
        event.preventDefault();
    });
});

// See https://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes
// We only list common keys below. Obscure keys are omitted and their use is discouraged.
var keyCodes = {
    8: 'backspace',
    9: 'tab',
    13: 'enter',
    16: 'shift',
    17: 'ctrl',
    18: 'alt',
    19: 'pause/break',
    20: 'caps lock',
    27: 'escape',
    32: 'spacebar',
    33: 'page up',
    34: 'page down',
    35: 'end',
    36: 'home',
    37: '&larr;',
    38: '&uarr;',
    39: '&rarr;',
    40: '&darr;',
    45: 'insert',
    46: 'delete',
    48: '0',
    49: '1',
    50: '2',
    51: '3',
    52: '4',
    53: '5',
    54: '6',
    55: '7',
    56: '8',
    57: '9',
    65: 'a',
    66: 'b',
    67: 'c',
    68: 'd',
    69: 'e',
    70: 'f',
    71: 'g',
    72: 'h',
    73: 'i',
    74: 'j',
    75: 'k',
    76: 'l',
    77: 'm',
    78: 'n',
    79: 'o',
    80: 'p',
    81: 'q',
    82: 'r',
    83: 's',
    84: 't',
    85: 'u',
    86: 'v',
    87: 'w',
    88: 'x',
    89: 'y',
    90: 'z',
    91: 'Left Windows Key / Left ⌘',
    92: 'Right Windows Key',
    93: 'Windows Menu / Right ⌘',
    96: 'numpad 0',
    97: 'numpad 1',
    98: 'numpad 2',
    99: 'numpad 3',
    100: 'numpad 4',
    101: 'numpad 5',
    102: 'numpad 6',
    103: 'numpad 7',
    104: 'numpad 8',
    105: 'numpad 9',
    106: 'multiply',
    107: 'add',
    109: 'subtract',
    110: 'decimal point',
    111: 'divide',
    112: 'f1',
    113: 'f2',
    114: 'f3',
    115: 'f4',
    116: 'f5',
    117: 'f6',
    118: 'f7',
    119: 'f8',
    120: 'f9',
    121: 'f10',
    122: 'f11',
    123: 'f12',
    124: 'f13',
    125: 'f14',
    126: 'f15',
    127: 'f16',
    128: 'f17',
    129: 'f18',
    130: 'f19',
    131: 'f20',
    132: 'f21',
    133: 'f22',
    134: 'f23',
    135: 'f24',
    144: 'num lock',
    145: 'scroll lock',
    186: '&semi;',
    187: '&equals;',
    188: '&comma;',
    189: '&hyphen;',
    190: '&period;',
    191: '&quest;',
    192: '&grave;',
    219: '&lsqb;',
    220: '&bsol;',
    221: '&rsqb;',
    222: '&apos;',
};
