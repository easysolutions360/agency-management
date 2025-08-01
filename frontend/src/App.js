import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Move FormInput component outside to prevent recreation on every render
const FormInput = ({ label, type = "text", value, onChange, required = true, options = null }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-2">
      {label}
    </label>
    {options ? (
      <select
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={value}
        onChange={onChange}
        required={required}
      >
        <option value="">Select {label}</option>
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    ) : (
      <input
        type={type}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={value}
        onChange={onChange}
        required={required}
      />
    )}
  </div>
);

// Move TabButton component outside to prevent recreation on every render
const TabButton = ({ tab, label, isActive, onClick }) => (
  <button
    className={`px-6 py-3 rounded-lg font-medium transition-colors ${
      isActive
        ? "bg-blue-600 text-white"
        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
    }`}
    onClick={onClick}
  >
    {label}
  </button>
);

const App = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [customers, setCustomers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [dashboardProjects, setDashboardProjects] = useState([]);
  const [expiringDomains, setExpiringDomains] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectDomains, setProjectDomains] = useState([]);
  const [domains, setDomains] = useState([]);
  const [domainsForRenewal, setDomainsForRenewal] = useState([]);
  const [customerPaymentSummaries, setCustomerPaymentSummaries] = useState([]);
  const [amcProjects, setAmcProjects] = useState([]);
  const [editingItem, setEditingItem] = useState(null);
  const [editingType, setEditingType] = useState(null);
  const [customerBalances, setCustomerBalances] = useState([]);
  const [businessFinancials, setBusinessFinancials] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerLedger, setCustomerLedger] = useState([]);
  const [paymentModal, setPaymentModal] = useState(false);
  const [renewalModal, setRenewalModal] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [passwordVisibility, setPasswordVisibility] = useState({}); // For toggling password visibility
  const [ledgerModal, setLedgerModal] = useState(false); // For customer ledger modal
  const [ledgerCurrentPage, setLedgerCurrentPage] = useState(1);
  const [ledgerPageSize] = useState(10);
  
  // Pagination states
  const [reportsTab, setReportsTab] = useState("customers");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState("");

  // Form states
  const [customerForm, setCustomerForm] = useState({
    name: "",
    phone: "",
    email: "",
    address: ""
  });

  const [projectForm, setProjectForm] = useState({
    customer_id: "",
    type: "",
    name: "",
    amount: "",
    amc_amount: "",
    start_date: "",
    end_date: ""
  });

  const [domainForm, setDomainForm] = useState({
    project_id: "",
    domain_name: "",
    hosting_provider: "",
    username: "",
    password: "",
    validity_date: "",
    renewal_amount: ""
  });

  const [paymentForm, setPaymentForm] = useState({
    customer_id: "",
    type: "",
    reference_id: "",
    amount: "",
    description: ""
  });

  const [renewalForm, setRenewalForm] = useState({
    new_validity_date: "",
    amount: "",
    payment_type: "client"
  });

  // API calls
  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`);
      setCustomers(response.data);
    } catch (error) {
      console.error("Error fetching customers:", error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  };

  const fetchDashboardProjects = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/projects`);
      setDashboardProjects(response.data);
    } catch (error) {
      console.error("Error fetching dashboard projects:", error);
    }
  };

  const fetchExpiringDomains = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/expiring-domains`);
      setExpiringDomains(response.data);
    } catch (error) {
      console.error("Error fetching expiring domains:", error);
    }
  };

  const fetchDomains = async () => {
    try {
      const response = await axios.get(`${API}/domains`);
      setDomains(response.data);
    } catch (error) {
      console.error("Error fetching domains:", error);
    }
  };

  const fetchProjectDomains = async (projectId) => {
    try {
      const response = await axios.get(`${API}/domains/project/${projectId}`);
      setProjectDomains(response.data);
    } catch (error) {
      console.error("Error fetching project domains:", error);
    }
  };

  const fetchAmcProjects = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/amc-projects`);
      setAmcProjects(response.data);
    } catch (error) {
      console.error("Error fetching AMC projects:", error);
    }
  };

  const fetchCustomerBalances = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/customer-balances`);
      setCustomerBalances(response.data);
    } catch (error) {
      console.error("Error fetching customer balances:", error);
    }
  };

  const fetchBusinessFinancials = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/business-financial-summary`);
      setBusinessFinancials(response.data);
    } catch (error) {
      console.error("Error fetching business financials:", error);
    }
  };

  const fetchCustomerLedger = async (customerId) => {
    try {
      const response = await axios.get(`${API}/ledger/customer/${customerId}`);
      setCustomerLedger(response.data);
    } catch (error) {
      console.error("Error fetching customer ledger:", error);
    }
  };

  const viewCustomerLedger = async (customerId, customerName) => {
    setSelectedCustomer({ id: customerId, name: customerName });
    setLedgerCurrentPage(1); // Reset to first page
    await fetchCustomerLedger(customerId);
    setLedgerModal(true); // Open the modal
  };

  const togglePasswordVisibility = (domainId) => {
    setPasswordVisibility(prev => ({
      ...prev,
      [domainId]: !prev[domainId]
    }));
  };

  // Helper function to check if domain is due for renewal (within 30 days)
  const isDomainDueForRenewal = (domain) => {
    const validityDate = new Date(domain.validity_date);
    const currentDate = new Date();
    const timeDifference = validityDate.getTime() - currentDate.getTime();
    const daysDifference = Math.ceil(timeDifference / (1000 * 3600 * 24));
    
    // Domain is due for renewal if it expires within 30 days or has already expired
    return daysDifference <= 30;
  };

  const fetchDomainsForRenewal = async () => {
    try {
      const response = await axios.get(`${API}/domains-due-renewal`);
      setDomainsForRenewal(response.data);
    } catch (error) {
      console.error("Error fetching domains for renewal:", error);
    }
  };

  const fetchCustomerPaymentSummaries = async () => {
    try {
      // For now, we'll create summaries from existing data
      const summaries = await Promise.all(
        customers.map(async (customer) => {
          try {
            const response = await axios.get(`${API}/customer-payment-summary/${customer.id}`);
            return response.data;
          } catch (error) {
            console.error(`Error fetching payment summary for ${customer.name}:`, error);
            return {
              customer_id: customer.id,
              customer_name: customer.name,
              total_projects: 0,
              total_project_amount: 0,
              total_paid_amount: 0,
              outstanding_amount: 0,
              credit_balance: 0,
              recent_payments: []
            };
          }
        })
      );
      setCustomerPaymentSummaries(summaries);
    } catch (error) {
      console.error("Error fetching customer payment summaries:", error);
    }
  };

  useEffect(() => {
    fetchCustomers();
    fetchProjects();
    fetchDashboardProjects();
    fetchExpiringDomains();
    fetchDomains();
    fetchDomainsForRenewal();
    fetchAmcProjects();
    fetchCustomerBalances();
    fetchBusinessFinancials();
  }, []);

  useEffect(() => {
    if (customers.length > 0) {
      fetchCustomerPaymentSummaries();
    }
  }, [customers]);

  const handleCustomerSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/customers`, customerForm);
      setCustomerForm({ name: "", phone: "", email: "", address: "" });
      fetchCustomers();
      alert("Customer added successfully!");
    } catch (error) {
      console.error("Error adding customer:", error);
      alert("Error adding customer");
    }
  };

  const handleProjectSubmit = async (e) => {
    e.preventDefault();
    try {
      const projectData = {
        ...projectForm,
        amount: parseFloat(projectForm.amount),
        amc_amount: parseFloat(projectForm.amc_amount) || 0
      };
      
      // Handle optional end_date - send null if empty, otherwise send the date
      if (projectForm.end_date && projectForm.end_date.trim() !== "") {
        projectData.end_date = projectForm.end_date;
      } else {
        projectData.end_date = null;
      }
      
      await axios.post(`${API}/projects`, projectData);
      setProjectForm({
        customer_id: "",
        type: "",
        name: "",
        amount: "",
        amc_amount: "",
        start_date: "",
        end_date: ""
      });
      fetchProjects();
      fetchDashboardProjects();
      alert("Project added successfully!");
    } catch (error) {
      console.error("Error adding project:", error);
      alert("Error adding project");
    }
  };

  const handleDomainSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/domains`, domainForm);
      setDomainForm({
        project_id: "",
        domain_name: "",
        hosting_provider: "",
        username: "",
        password: "",
        validity_date: "",
        renewal_amount: ""
      });
      fetchDashboardProjects();
      fetchExpiringDomains();
      fetchDomains();
      if (selectedProject) {
        fetchProjectDomains(selectedProject);
      }
      alert("Domain/Hosting added successfully!");
    } catch (error) {
      console.error("Error adding domain:", error);
      alert("Error adding domain");
    }
  };

  const handlePaymentSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/payments`, paymentForm);
      setPaymentForm({
        customer_id: "",
        type: "",
        reference_id: "",
        amount: "",
        description: ""
      });
      setPaymentModal(false);
      fetchProjects();
      fetchDashboardProjects();
      fetchCustomerBalances();
      fetchCustomerPaymentSummaries();
      alert("Payment recorded successfully!");
    } catch (error) {
      console.error("Error recording payment:", error);
      alert("Error recording payment");
    }
  };

  const handleRenewalSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/domain-renewal/${selectedDomain.id}`, renewalForm);
      setRenewalForm({
        new_validity_date: "",
        amount: "",
        payment_type: "client"
      });
      setRenewalModal(false);
      setSelectedDomain(null);
      fetchDomains();
      fetchDashboardProjects();
      fetchExpiringDomains();
      fetchCustomerBalances();
      alert("Domain renewed successfully!");
    } catch (error) {
      console.error("Error renewing domain:", error);
      alert("Error renewing domain");
    }
  };

  const handleAMCPayment = async (amcProject) => {
    const amcAmount = amcProject.amc_amount || 0;
    if (amcAmount <= 0) {
      alert("No AMC amount set for this project. Please update the project with AMC amount.");
      return;
    }
    
    const confirmMessage = `Record AMC payment of ₹${amcAmount.toLocaleString()} for project: ${amcProject.project_name}?`;
    if (window.confirm(confirmMessage)) {
      try {
        await axios.post(`${API}/amc-payment/${amcProject.project_id}`, {
          project_id: amcProject.project_id,
          amount: amcAmount
        });
        
        fetchAmcProjects();
        fetchCustomerBalances();
        fetchCustomerPaymentSummaries();
        alert(`AMC payment of ₹${amcAmount.toLocaleString()} recorded successfully! AMC renewed for 1 year.`);
      } catch (error) {
        console.error("Error recording AMC payment:", error);
        alert("Error recording AMC payment");
      }
    }
  };

  const openPaymentModal = (customer_id, type, reference_id, description) => {
    setPaymentForm({
      customer_id,
      type,
      reference_id,
      amount: "",
      description
    });
    setPaymentModal(true);
  };

  const openRenewalModal = (domain) => {
    setSelectedDomain(domain);
    setRenewalModal(true);
  };

  const handleDomainRenewal = async (domain, paymentType) => {
    try {
      const confirmMessage = paymentType === 'agency' 
        ? `Are you sure the agency will pay for ${domain.domain_name} renewal? This will be added to customer's debt.`
        : `Confirm that the client will pay for ${domain.domain_name} renewal.`;
      
      if (window.confirm(confirmMessage)) {
        // Use domain_id from the API response (for domainsForRenewal) or id (for regular domains)
        const domainId = domain.domain_id || domain.id;
        
        await axios.post(`${API}/domain-renewal/${domainId}`, {
          domain_id: domainId,
          payment_type: paymentType,
          notes: `Domain renewal - ${paymentType === 'agency' ? 'Agency paid' : 'Client paid'}`
        });
        
        fetchDomainsForRenewal();
        fetchDomains();
        fetchExpiringDomains();
        fetchCustomerBalances();
        fetchCustomerPaymentSummaries();
        
        alert(`Domain ${domain.domain_name} renewed successfully! ${paymentType === 'agency' ? 'Added to customer debt.' : ''}`);
      }
    } catch (error) {
      console.error("Error renewing domain:", error);
      alert("Error renewing domain");
    }
  };

  // Delete functions
  const handleDeleteCustomer = async (customerId) => {
    if (window.confirm("Are you sure you want to delete this customer?")) {
      try {
        await axios.delete(`${API}/customers/${customerId}`);
        fetchCustomers();
        fetchDashboardProjects();
        alert("Customer deleted successfully!");
      } catch (error) {
        console.error("Error deleting customer:", error);
        alert("Error deleting customer");
      }
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (window.confirm("Are you sure you want to delete this project?")) {
      try {
        await axios.delete(`${API}/projects/${projectId}`);
        fetchProjects();
        fetchDashboardProjects();
        fetchAmcProjects();
        alert("Project deleted successfully!");
      } catch (error) {
        console.error("Error deleting project:", error);
        alert("Error deleting project");
      }
    }
  };

  const handleDeleteDomain = async (domainId) => {
    if (window.confirm("Are you sure you want to delete this domain?")) {
      try {
        await axios.delete(`${API}/domains/${domainId}`);
        fetchDomains();
        fetchDashboardProjects();
        fetchExpiringDomains();
        alert("Domain deleted successfully!");
      } catch (error) {
        console.error("Error deleting domain:", error);
        alert("Error deleting domain");
      }
    }
  };

  // Edit functions
  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingType === "customer") {
        await axios.put(`${API}/customers/${editingItem.id}`, editingItem);
        fetchCustomers();
        fetchDashboardProjects();
      } else if (editingType === "project") {
        const projectData = {
          ...editingItem,
          amount: parseFloat(editingItem.amount),
          amc_amount: parseFloat(editingItem.amc_amount) || 0
        };
        
        // Handle optional end_date - send null if empty, otherwise send the date
        if (editingItem.end_date && editingItem.end_date.trim() !== "") {
          projectData.end_date = editingItem.end_date;
        } else {
          projectData.end_date = null;
        }
        
        await axios.put(`${API}/projects/${editingItem.id}`, projectData);
        fetchProjects();
        fetchDashboardProjects();
        fetchAmcProjects();
      } else if (editingType === "domain") {
        await axios.put(`${API}/domains/${editingItem.id}`, editingItem);
        fetchDomains();
        fetchDashboardProjects();
        fetchExpiringDomains();
      }
      setEditingItem(null);
      setEditingType(null);
      alert("Updated successfully!");
    } catch (error) {
      console.error("Error updating:", error);
      alert("Error updating");
    }
  };

  const handleEditCancel = () => {
    setEditingItem(null);
    setEditingType(null);
  };

  // Pagination helper functions
  const getFilteredData = (data, searchTerm) => {
    if (!searchTerm) return data;
    return data.filter(item => 
      Object.values(item).some(value => 
        value.toString().toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  };

  const getPaginatedData = (data, currentPage, pageSize) => {
    if (pageSize === "all") return data;
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return data.slice(startIndex, endIndex);
  };

  const getTotalPages = (totalItems, pageSize) => {
    if (pageSize === "all") return 1;
    return Math.ceil(totalItems / pageSize);
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handlePageSizeChange = (newPageSize) => {
    setPageSize(newPageSize);
    setCurrentPage(1);
  };

  const handleSearchChange = (newSearchTerm) => {
    setSearchTerm(newSearchTerm);
    setCurrentPage(1);
  };

  const handleReportsTabChange = (newTab) => {
    setReportsTab(newTab);
    setCurrentPage(1);
    setSearchTerm("");
  };

  // Pagination component
  const PaginationControls = ({ currentPage, totalPages, onPageChange, totalItems, pageSize, onPageSizeChange }) => (
    <div className="flex flex-col sm:flex-row justify-between items-center mt-6 space-y-4 sm:space-y-0">
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-700">
          Showing {pageSize === "all" ? totalItems : Math.min(pageSize, totalItems)} of {totalItems} results
        </span>
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-700">Show:</label>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(e.target.value === "all" ? "all" : parseInt(e.target.value))}
            className="px-2 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value={10}>10</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={500}>500</option>
            <option value={1000}>1000</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>
      
      {pageSize !== "all" && totalPages > 1 && (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          <div className="flex space-x-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => onPageChange(pageNum)}
                  className={`px-3 py-1 rounded-md ${
                    currentPage === pageNum
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>
          
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Business Dashboard</h2>
        
        {/* Business Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800">Total Customers</h3>
            <p className="text-3xl font-bold text-blue-600">{customers.length}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800">Total Projects</h3>
            <p className="text-3xl font-bold text-green-600">{projects.length}</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-red-800">Expiring Domains</h3>
            <p className="text-3xl font-bold text-red-600">{expiringDomains.length}</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-purple-800">AMC Due</h3>
            <p className="text-3xl font-bold text-purple-600">{amcProjects.length}</p>
          </div>
        </div>

        {/* Financial Summary Cards */}
        {businessFinancials && (
          <div className="mb-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">💰 Financial Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-200">
                <h4 className="text-sm font-semibold text-emerald-800">Total Project Value</h4>
                <p className="text-2xl font-bold text-emerald-600">₹{businessFinancials.total_project_value.toLocaleString()}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h4 className="text-sm font-semibold text-green-800">Total Received</h4>
                <p className="text-2xl font-bold text-green-600">₹{businessFinancials.total_received.toLocaleString()}</p>
                <p className="text-xs text-green-700">{businessFinancials.payment_collection_rate}% collection rate</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <h4 className="text-sm font-semibold text-orange-800">Outstanding Amount</h4>
                <p className="text-2xl font-bold text-orange-600">₹{businessFinancials.total_outstanding.toLocaleString()}</p>
              </div>
              <div className="bg-cyan-50 p-4 rounded-lg border border-cyan-200">
                <h4 className="text-sm font-semibold text-cyan-800">Customer Credit</h4>
                <p className="text-2xl font-bold text-cyan-600">₹{businessFinancials.total_customer_credit.toLocaleString()}</p>
              </div>
            </div>
            
            {/* Net Revenue & Collection Rate */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
                <h4 className="text-lg font-semibold text-indigo-800">Net Revenue</h4>
                <p className="text-3xl font-bold text-indigo-600">₹{businessFinancials.net_revenue.toLocaleString()}</p>
                <p className="text-sm text-indigo-700">Total received + customer credits</p>
              </div>
              <div className="bg-teal-50 p-4 rounded-lg border border-teal-200">
                <h4 className="text-lg font-semibold text-teal-800">Project Completion</h4>
                <p className="text-3xl font-bold text-teal-600">{businessFinancials.project_completion_rate}%</p>
                <p className="text-sm text-teal-700">Revenue collected vs total project value</p>
              </div>
            </div>
          </div>
        )}

        {/* Top Customers */}
        {businessFinancials && businessFinancials.top_customers && businessFinancials.top_customers.length > 0 && (
          <div className="mb-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">🏆 Top Customers by Project Value</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="space-y-2">
                {businessFinancials.top_customers.map((customer, index) => (
                  <div key={index} className="flex justify-between items-center py-2 px-3 bg-white rounded border">
                    <div>
                      <span className="font-medium">{customer.customer_name}</span>
                      <span className="text-sm text-gray-600 ml-2">({customer.project_count} projects)</span>
                    </div>
                    <span className="font-bold text-green-600">₹{customer.total_amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {expiringDomains.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-semibold text-red-800 mb-3">⚠️ Domains Expiring Soon</h3>
            <div className="space-y-2">
              {expiringDomains.map((domain, index) => (
                <div key={index} className="bg-white p-3 rounded border">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{domain.domain_name}</p>
                      <p className="text-sm text-gray-600">
                        {domain.customer_name} - {domain.project_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-red-600 font-medium">
                        Expires: {new Date(domain.validity_date).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-red-500">
                        {domain.days_remaining} days remaining
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="overflow-x-auto">
          <h3 className="text-xl font-bold text-gray-800 mb-4">📊 Recent Projects</h3>
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left">Customer</th>
                <th className="px-4 py-2 text-left">Project</th>
                <th className="px-4 py-2 text-left">Type</th>
                <th className="px-4 py-2 text-left">Amount</th>
                <th className="px-4 py-2 text-left">Duration</th>
                <th className="px-4 py-2 text-left">Domains</th>
              </tr>
            </thead>
            <tbody>
              {dashboardProjects.map((project) => (
                <tr key={project.id} className="border-b">
                  <td className="px-4 py-2">
                    <div>
                      <p className="font-medium">{project.customer_name}</p>
                      <p className="text-sm text-gray-600">{project.customer_email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2 font-medium">{project.name}</td>
                  <td className="px-4 py-2">{project.type}</td>
                  <td className="px-4 py-2">₹{project.amount.toLocaleString()}</td>
                  <td className="px-4 py-2">
                    <div className="text-sm">
                      <p>{new Date(project.start_date).toLocaleDateString()}</p>
                      <p>{new Date(project.end_date).toLocaleDateString()}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <div className="space-y-1">
                      {project.domains.map((domain, index) => (
                        <div key={index} className="text-sm">
                          <p className="font-medium">{domain.domain_name}</p>
                          <p className="text-gray-600">{domain.hosting_provider}</p>
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderCustomerForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Customer</h2>
      <form onSubmit={handleCustomerSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Customer Name"
            value={customerForm.name}
            onChange={(e) => setCustomerForm({ ...customerForm, name: e.target.value })}
          />
          <FormInput
            label="Phone Number"
            type="tel"
            value={customerForm.phone}
            onChange={(e) => setCustomerForm({ ...customerForm, phone: e.target.value })}
          />
          <FormInput
            label="Email Address"
            type="email"
            value={customerForm.email}
            onChange={(e) => setCustomerForm({ ...customerForm, email: e.target.value })}
          />
          <FormInput
            label="Address"
            value={customerForm.address}
            onChange={(e) => setCustomerForm({ ...customerForm, address: e.target.value })}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
        >
          Add Customer
        </button>
      </form>
    </div>
  );

  const renderProjectForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Project</h2>
      <form onSubmit={handleProjectSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Customer"
            value={projectForm.customer_id}
            onChange={(e) => setProjectForm({ ...projectForm, customer_id: e.target.value })}
            options={customers.map(customer => ({
              value: customer.id,
              label: `${customer.name} - ${customer.email}`
            }))}
          />
          <FormInput
            label="Project Type"
            value={projectForm.type}
            onChange={(e) => setProjectForm({ ...projectForm, type: e.target.value })}
          />
          <FormInput
            label="Project Name"
            value={projectForm.name}
            onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
          />
          <FormInput
            label="Project Amount"
            type="number"
            value={projectForm.amount}
            onChange={(e) => setProjectForm({ ...projectForm, amount: e.target.value })}
          />
          <FormInput
            label="AMC Amount"
            type="number"
            value={projectForm.amc_amount}
            onChange={(e) => setProjectForm({ ...projectForm, amc_amount: e.target.value })}
            required={false}
          />
          <FormInput
            label="Start Date"
            type="date"
            value={projectForm.start_date}
            onChange={(e) => setProjectForm({ ...projectForm, start_date: e.target.value })}
          />
          <FormInput
            label="End Date"
            type="date"
            value={projectForm.end_date}
            onChange={(e) => setProjectForm({ ...projectForm, end_date: e.target.value })}
            required={false}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
        >
          Add Project
        </button>
      </form>
    </div>
  );

  const renderDomainForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add Domain/Hosting</h2>
      <form onSubmit={handleDomainSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Project"
            value={domainForm.project_id}
            onChange={(e) => setDomainForm({ ...domainForm, project_id: e.target.value })}
            options={projects.map(project => ({
              value: project.id,
              label: `${project.name} - ${project.type}`
            }))}
          />
          <FormInput
            label="Domain Name"
            value={domainForm.domain_name}
            onChange={(e) => setDomainForm({ ...domainForm, domain_name: e.target.value })}
          />
          <FormInput
            label="Hosting Provider"
            value={domainForm.hosting_provider}
            onChange={(e) => setDomainForm({ ...domainForm, hosting_provider: e.target.value })}
          />
          <FormInput
            label="Username"
            value={domainForm.username}
            onChange={(e) => setDomainForm({ ...domainForm, username: e.target.value })}
          />
          <FormInput
            label="Password"
            type="password"
            value={domainForm.password}
            onChange={(e) => setDomainForm({ ...domainForm, password: e.target.value })}
          />
          <FormInput
            label="Validity Date"
            type="date"
            value={domainForm.validity_date}
            onChange={(e) => setDomainForm({ ...domainForm, validity_date: e.target.value })}
          />
          <FormInput
            label="Renewal Amount"
            type="number"
            value={domainForm.renewal_amount}
            onChange={(e) => setDomainForm({ ...domainForm, renewal_amount: e.target.value })}
            required={false}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors"
        >
          Add Domain/Hosting
        </button>
      </form>
    </div>
  );

  const renderReports = () => {
    // Get current data based on active reports tab
    let currentData = [];
    if (reportsTab === "customers") {
      currentData = customers;
    } else if (reportsTab === "projects") {
      currentData = projects;
    } else if (reportsTab === "domains") {
      currentData = domains;
    } else if (reportsTab === "renewals") {
      currentData = domainsForRenewal;
    } else if (reportsTab === "payments") {
      currentData = customerPaymentSummaries;
    }

    // Apply search filter
    const filteredData = getFilteredData(currentData, searchTerm);
    
    // Apply pagination
    const paginatedData = getPaginatedData(filteredData, currentPage, pageSize);
    
    // Calculate total pages
    const totalPages = getTotalPages(filteredData.length, pageSize);

    return (
      <div className="space-y-6">
        {/* Payment Modal */}
        {paymentModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-bold mb-4">Record Payment</h3>
              <form onSubmit={handlePaymentSubmit} className="space-y-4">
                <FormInput
                  label="Amount"
                  type="number"
                  value={paymentForm.amount}
                  onChange={(e) => setPaymentForm({...paymentForm, amount: e.target.value})}
                />
                <FormInput
                  label="Description"
                  value={paymentForm.description}
                  onChange={(e) => setPaymentForm({...paymentForm, description: e.target.value})}
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
                  >
                    Record Payment
                  </button>
                  <button
                    type="button"
                    onClick={() => setPaymentModal(false)}
                    className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Renewal Modal */}
        {renewalModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-bold mb-4">Renew Domain: {selectedDomain?.domain_name}</h3>
              <form onSubmit={handleRenewalSubmit} className="space-y-4">
                <FormInput
                  label="New Validity Date"
                  type="date"
                  value={renewalForm.new_validity_date}
                  onChange={(e) => setRenewalForm({...renewalForm, new_validity_date: e.target.value})}
                />
                <FormInput
                  label="Renewal Amount"
                  type="number"
                  value={renewalForm.amount}
                  onChange={(e) => setRenewalForm({...renewalForm, amount: e.target.value})}
                />
                <FormInput
                  label="Payment Type"
                  value={renewalForm.payment_type}
                  onChange={(e) => setRenewalForm({...renewalForm, payment_type: e.target.value})}
                  options={[
                    { value: "client", label: "Client Paid" },
                    { value: "agency", label: "Agency Paid (Add to Customer Credit)" }
                  ]}
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
                  >
                    Renew Domain
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setRenewalModal(false);
                      setSelectedDomain(null);
                    }}
                    className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {editingItem && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-bold mb-4">Edit {editingType}</h3>
              <form onSubmit={handleEditSubmit} className="space-y-4">
                {editingType === "customer" && (
                  <>
                    <FormInput
                      label="Name"
                      value={editingItem.name}
                      onChange={(e) => setEditingItem({...editingItem, name: e.target.value})}
                    />
                    <FormInput
                      label="Phone"
                      value={editingItem.phone}
                      onChange={(e) => setEditingItem({...editingItem, phone: e.target.value})}
                    />
                    <FormInput
                      label="Email"
                      value={editingItem.email}
                      onChange={(e) => setEditingItem({...editingItem, email: e.target.value})}
                    />
                    <FormInput
                      label="Address"
                      value={editingItem.address}
                      onChange={(e) => setEditingItem({...editingItem, address: e.target.value})}
                    />
                  </>
                )}
                {editingType === "project" && (
                  <>
                    <FormInput
                      label="Type"
                      value={editingItem.type}
                      onChange={(e) => setEditingItem({...editingItem, type: e.target.value})}
                    />
                    <FormInput
                      label="Name"
                      value={editingItem.name}
                      onChange={(e) => setEditingItem({...editingItem, name: e.target.value})}
                    />
                    <FormInput
                      label="Amount"
                      type="number"
                      value={editingItem.amount}
                      onChange={(e) => setEditingItem({...editingItem, amount: e.target.value})}
                    />
                    <FormInput
                      label="AMC Amount"
                      type="number"
                      value={editingItem.amc_amount || ""}
                      onChange={(e) => setEditingItem({...editingItem, amc_amount: e.target.value})}
                      required={false}
                    />
                    <FormInput
                      label="Start Date"
                      type="date"
                      value={editingItem.start_date}
                      onChange={(e) => setEditingItem({...editingItem, start_date: e.target.value})}
                    />
                    <FormInput
                      label="End Date"
                      type="date"
                      value={editingItem.end_date || ""}
                      onChange={(e) => setEditingItem({...editingItem, end_date: e.target.value})}
                      required={false}
                    />
                  </>
                )}
                {editingType === "domain" && (
                  <>
                    <FormInput
                      label="Domain Name"
                      value={editingItem.domain_name}
                      onChange={(e) => setEditingItem({...editingItem, domain_name: e.target.value})}
                    />
                    <FormInput
                      label="Hosting Provider"
                      value={editingItem.hosting_provider}
                      onChange={(e) => setEditingItem({...editingItem, hosting_provider: e.target.value})}
                    />
                    <FormInput
                      label="Username"
                      value={editingItem.username}
                      onChange={(e) => setEditingItem({...editingItem, username: e.target.value})}
                    />
                    <FormInput
                      label="Password"
                      type="password"
                      value={editingItem.password}
                      onChange={(e) => setEditingItem({...editingItem, password: e.target.value})}
                    />
                    <FormInput
                      label="Validity Date"
                      type="date"
                      value={editingItem.validity_date}
                      onChange={(e) => setEditingItem({...editingItem, validity_date: e.target.value})}
                    />
                  </>
                )}
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={handleEditCancel}
                    className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Reports Main Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 sm:mb-0">Reports</h2>
            
            {/* Search Bar */}
            <div className="w-full sm:w-auto">
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Reports Tabs */}
          <div className="flex flex-wrap gap-2 mb-6">
            <button
              onClick={() => handleReportsTabChange("customers")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                reportsTab === "customers"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Customers ({customers.length})
            </button>
            <button
              onClick={() => handleReportsTabChange("projects")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                reportsTab === "projects"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Projects ({projects.length})
            </button>
            <button
              onClick={() => handleReportsTabChange("domains")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                reportsTab === "domains"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Domains ({domains.length})
            </button>
            <button
              onClick={() => handleReportsTabChange("renewals")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                reportsTab === "renewals"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Domain Renewals ({domainsForRenewal.length})
            </button>
            <button
              onClick={() => handleReportsTabChange("payments")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                reportsTab === "payments"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Customer Payments
            </button>
          </div>

          {/* Table Content */}
          <div className="overflow-x-auto">
            {reportsTab === "customers" && (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Name</th>
                    <th className="px-4 py-2 text-left">Email</th>
                    <th className="px-4 py-2 text-left">Phone</th>
                    <th className="px-4 py-2 text-left">Address</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((customer) => (
                    <tr key={customer.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{customer.name}</td>
                      <td className="px-4 py-2">{customer.email}</td>
                      <td className="px-4 py-2">{customer.phone}</td>
                      <td className="px-4 py-2">{customer.address}</td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setEditingItem(customer);
                              setEditingType("customer");
                            }}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteCustomer(customer.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {reportsTab === "projects" && (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Project Name</th>
                    <th className="px-4 py-2 text-left">Type</th>
                    <th className="px-4 py-2 text-left">Amount</th>
                    <th className="px-4 py-2 text-left">Paid</th>
                    <th className="px-4 py-2 text-left">Status</th>
                    <th className="px-4 py-2 text-left">Start Date</th>
                    <th className="px-4 py-2 text-left">End Date</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((project) => (
                    <tr key={project.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{project.name}</td>
                      <td className="px-4 py-2">{project.type}</td>
                      <td className="px-4 py-2">₹{project.amount.toLocaleString()}</td>
                      <td className="px-4 py-2">₹{(project.paid_amount || 0).toLocaleString()}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          project.payment_status === "paid" 
                            ? "bg-green-100 text-green-800"
                            : project.payment_status === "partial"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                        }`}>
                          {project.payment_status || "pending"}
                        </span>
                      </td>
                      <td className="px-4 py-2">{new Date(project.start_date).toLocaleDateString()}</td>
                      <td className="px-4 py-2">
                        {project.end_date ? new Date(project.end_date).toLocaleDateString() : "Not set"}
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setEditingItem(project);
                              setEditingType("project");
                            }}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteProject(project.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                          >
                            Delete
                          </button>
                          {project.payment_status !== "paid" && (
                            <button
                              onClick={() => openPaymentModal(
                                project.customer_id, 
                                "project_advance", 
                                project.id, 
                                `Payment for ${project.name}`
                              )}
                              className="bg-green-500 text-white px-2 py-1 rounded text-sm hover:bg-green-600"
                            >
                              Add Payment
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {reportsTab === "domains" && (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Domain Name</th>
                    <th className="px-4 py-2 text-left">Hosting Provider</th>
                    <th className="px-4 py-2 text-left">Username</th>
                    <th className="px-4 py-2 text-left">Password</th>
                    <th className="px-4 py-2 text-left">Validity Date</th>
                    <th className="px-4 py-2 text-left">Renewal Amount</th>
                    <th className="px-4 py-2 text-left">Status</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((domain) => (
                    <tr key={domain.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{domain.domain_name}</td>
                      <td className="px-4 py-2">{domain.hosting_provider}</td>
                      <td className="px-4 py-2">{domain.username}</td>
                      <td className="px-4 py-2">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono">
                            {passwordVisibility[domain.id] ? domain.password : '••••••••'}
                          </span>
                          <button
                            onClick={() => togglePasswordVisibility(domain.id)}
                            className="text-blue-500 hover:text-blue-700 text-sm"
                            title={passwordVisibility[domain.id] ? "Hide password" : "Show password"}
                          >
                            {passwordVisibility[domain.id] ? '👁️‍🗨️' : '👁️'}
                          </button>
                        </div>
                      </td>
                      <td className="px-4 py-2">{new Date(domain.validity_date).toLocaleDateString()}</td>
                      <td className="px-4 py-2">₹{(domain.renewal_amount || 0).toLocaleString()}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          domain.renewal_status === "renewed" 
                            ? "bg-green-100 text-green-800"
                            : domain.renewal_status === "due"
                            ? "bg-red-100 text-red-800"
                            : "bg-blue-100 text-blue-800"
                        }`}>
                          {domain.renewal_status || "active"}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setEditingItem(domain);
                              setEditingType("domain");
                            }}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteDomain(domain.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                          >
                            Delete
                          </button>
                          {isDomainDueForRenewal(domain) ? (
                            <button
                              onClick={() => openRenewalModal(domain)}
                              className="bg-green-500 text-white px-2 py-1 rounded text-sm hover:bg-green-600"
                            >
                              Renew
                            </button>
                          ) : (
                            <button
                              disabled
                              className="bg-gray-400 text-white px-2 py-1 rounded text-sm cursor-not-allowed opacity-50"
                              title="Domain renewal available only within 30 days of expiry"
                            >
                              Renew
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {reportsTab === "renewals" && (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Domain Name</th>
                    <th className="px-4 py-2 text-left">Customer</th>
                    <th className="px-4 py-2 text-left">Project</th>
                    <th className="px-4 py-2 text-left">Validity Date</th>
                    <th className="px-4 py-2 text-left">Days Until Expiry</th>
                    <th className="px-4 py-2 text-left">Renewal Amount</th>
                    <th className="px-4 py-2 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((domain) => (
                    <tr key={domain.domain_id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{domain.domain_name}</td>
                      <td className="px-4 py-2">{domain.customer_name}</td>
                      <td className="px-4 py-2">{domain.project_name}</td>
                      <td className="px-4 py-2">{new Date(domain.validity_date).toLocaleDateString()}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          domain.is_expired 
                            ? "bg-red-100 text-red-800"
                            : domain.days_until_expiry <= 7
                            ? "bg-orange-100 text-orange-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}>
                          {domain.is_expired ? "EXPIRED" : `${domain.days_until_expiry} days`}
                        </span>
                      </td>
                      <td className="px-4 py-2">₹{(domain.renewal_amount || 0).toLocaleString()}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          domain.is_expired 
                            ? "bg-red-100 text-red-800"
                            : "bg-blue-100 text-blue-800"
                        }`}>
                          {domain.is_expired ? "Needs Renewal" : "Due Soon"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {reportsTab === "payments" && (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Customer</th>
                    <th className="px-4 py-2 text-left">Projects</th>
                    <th className="px-4 py-2 text-left">Total Amount</th>
                    <th className="px-4 py-2 text-left">Paid Amount</th>
                    <th className="px-4 py-2 text-left">Outstanding</th>
                    <th className="px-4 py-2 text-left">Credit Balance</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((summary) => (
                    <tr key={summary.customer_id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{summary.customer_name}</td>
                      <td className="px-4 py-2">{summary.total_projects}</td>
                      <td className="px-4 py-2">₹{(summary.total_project_amount || 0).toLocaleString()}</td>
                      <td className="px-4 py-2 text-green-600">₹{(summary.total_paid_amount || 0).toLocaleString()}</td>
                      <td className="px-4 py-2">
                        <span className={`font-medium ${
                          (summary.outstanding_amount || 0) > 0 
                            ? "text-red-600" 
                            : "text-gray-600"
                        }`}>
                          ₹{(summary.outstanding_amount || 0).toLocaleString()}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        <span className={`font-medium ${
                          (summary.credit_balance || 0) < 0 
                            ? "text-red-600" 
                            : summary.credit_balance > 0
                            ? "text-green-600"
                            : "text-gray-600"
                        }`}>
                          ₹{(summary.credit_balance || 0).toLocaleString()}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => viewCustomerLedger(summary.customer_id, summary.customer_name)}
                            className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                          >
                            View Ledger
                          </button>
                          <button
                            onClick={() => openPaymentModal(summary.customer_id, 'project_advance', '', `Payment for ${summary.customer_name}`)}
                            className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                          >
                            Add Payment
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Empty State */}
          {paginatedData.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">
                {searchTerm ? "No results found for your search." : `No ${reportsTab} found.`}
              </p>
            </div>
          )}

          {/* Pagination Controls */}
          <PaginationControls
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
            totalItems={filteredData.length}
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
        </div>
      </div>
    );
  };

  const renderCustomerLedgerTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Customer Ledger Management</h2>
        <p className="text-gray-600 mb-6">
          Select a customer to view their complete ledger with all transactions
        </p>
        
        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left">Customer Name</th>
                <th className="px-4 py-2 text-left">Email</th>
                <th className="px-4 py-2 text-left">Phone</th>
                <th className="px-4 py-2 text-left">Outstanding Amount</th>
                <th className="px-4 py-2 text-left">Credit Balance</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {customerPaymentSummaries.map((summary) => (
                <tr key={summary.customer_id} className="border-b">
                  <td className="px-4 py-2 font-medium">{summary.customer_name}</td>
                  <td className="px-4 py-2">{customers.find(c => c.id === summary.customer_id)?.email || 'N/A'}</td>
                  <td className="px-4 py-2">{customers.find(c => c.id === summary.customer_id)?.phone || 'N/A'}</td>
                  <td className="px-4 py-2">
                    <span className={`font-medium ${
                      summary.outstanding_amount > 0 ? "text-red-600" : "text-gray-600"
                    }`}>
                      ₹{(summary.outstanding_amount || 0).toLocaleString()}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    <span className={`font-medium ${
                      summary.credit_balance > 0 ? "text-green-600" : "text-gray-600"
                    }`}>
                      ₹{(summary.credit_balance || 0).toLocaleString()}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => viewCustomerLedger(summary.customer_id, summary.customer_name)}
                      className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                    >
                      View Complete Ledger
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderAMC = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">AMC (Annual Maintenance Contract) Tracker</h2>
        <p className="text-gray-600 mb-6">
          This section shows projects that are due for AMC renewal (1 year after project completion)
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800">Total AMC Due</h3>
            <p className="text-3xl font-bold text-blue-600">{amcProjects.length}</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-red-800">Overdue AMC</h3>
            <p className="text-3xl font-bold text-red-600">
              {amcProjects.filter(p => p.is_overdue).length}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800">Upcoming AMC</h3>
            <p className="text-3xl font-bold text-green-600">
              {amcProjects.filter(p => !p.is_overdue).length}
            </p>
          </div>
        </div>

        {/* Search Box */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search AMC projects by project name, customer name, or type..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left">Project</th>
                <th className="px-4 py-2 text-left">Customer</th>
                <th className="px-4 py-2 text-left">AMC Amount</th>
                <th className="px-4 py-2 text-left">Project End Date</th>
                <th className="px-4 py-2 text-left">AMC Due Date</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {amcProjects
                .filter(project => 
                  project.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  project.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  project.project_type.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .map((amcProject, index) => (
                <tr key={index} className="border-b">
                  <td className="px-4 py-2">
                    <div>
                      <p className="font-medium">{amcProject.project_name}</p>
                      <p className="text-sm text-gray-600">{amcProject.project_type}</p>
                      <p className="text-sm text-gray-600">₹{amcProject.project_amount.toLocaleString()}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <div>
                      <p className="font-medium">{amcProject.customer_name}</p>
                      <p className="text-sm text-gray-600">{amcProject.customer_email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <p className="font-medium text-green-600">
                      ₹{(amcProject.amc_amount || 0).toLocaleString()}
                    </p>
                  </td>
                  <td className="px-4 py-2">
                    {new Date(amcProject.project_end_date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2">
                    {new Date(amcProject.amc_due_date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded text-sm font-medium ${
                      amcProject.is_overdue 
                        ? "bg-red-100 text-red-800" 
                        : amcProject.days_until_amc <= 7
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-green-100 text-green-800"
                    }`}>
                      {amcProject.is_overdue 
                        ? `Overdue by ${Math.abs(amcProject.days_until_amc)} days`
                        : amcProject.days_until_amc === 0
                        ? "Due Today"
                        : `Due in ${amcProject.days_until_amc} days`
                      }
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleAMCPayment(amcProject)}
                        className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                      >
                        Record Payment
                      </button>
                      <a
                        href={`tel:${amcProject.customer_phone}`}
                        className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                        title="Call Customer"
                      >
                        📞
                      </a>
                      <a
                        href={`mailto:${amcProject.customer_email}`}
                        className="bg-purple-500 text-white px-2 py-1 rounded text-sm hover:bg-purple-600"
                        title="Email Customer"
                      >
                        ✉️
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {amcProjects.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>No AMC renewals due in the next 30 days</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Agency Management System</h1>
        
        <div className="flex flex-wrap gap-4 mb-8">
          <TabButton
            tab="dashboard"
            label="Dashboard"
            isActive={activeTab === "dashboard"}
            onClick={() => setActiveTab("dashboard")}
          />
          <TabButton
            tab="customers"
            label="Add Customer"
            isActive={activeTab === "customers"}
            onClick={() => setActiveTab("customers")}
          />
          <TabButton
            tab="projects"
            label="Add Project"
            isActive={activeTab === "projects"}
            onClick={() => setActiveTab("projects")}
          />
          <TabButton
            tab="domains"
            label="Add Domain/Hosting"
            isActive={activeTab === "domains"}
            onClick={() => setActiveTab("domains")}
          />
          <TabButton
            tab="reports"
            label="Reports"
            isActive={activeTab === "reports"}
            onClick={() => setActiveTab("reports")}
          />
          <TabButton
            tab="amc"
            label="AMC Tracker"
            isActive={activeTab === "amc"}
            onClick={() => setActiveTab("amc")}
          />
          <TabButton
            tab="ledger"
            label="Customer Ledger"
            isActive={activeTab === "ledger"}
            onClick={() => setActiveTab("ledger")}
          />
        </div>

        {activeTab === "dashboard" && renderDashboard()}
        {activeTab === "customers" && renderCustomerForm()}
        {activeTab === "projects" && renderProjectForm()}
        {activeTab === "domains" && renderDomainForm()}
        {activeTab === "reports" && renderReports()}
        {activeTab === "amc" && renderAMC()}
        {activeTab === "ledger" && renderCustomerLedgerTab()}

        {/* Customer Ledger Modal */}
        {ledgerModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-hidden mx-4">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">
                  Customer Ledger - {selectedCustomer?.name}
                </h2>
                <button
                  onClick={() => setLedgerModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              
              <div className="overflow-y-auto max-h-[70vh]">
                {customerLedger.length > 0 ? (
                  <>
                    <table className="w-full table-auto mb-4">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="px-4 py-2 text-left">Date</th>
                          <th className="px-4 py-2 text-left">Type</th>
                          <th className="px-4 py-2 text-left">Amount</th>
                          <th className="px-4 py-2 text-left">Description</th>
                          <th className="px-4 py-2 text-left">Balance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(() => {
                          const startIndex = (ledgerCurrentPage - 1) * ledgerPageSize;
                          const endIndex = startIndex + ledgerPageSize;
                          const paginatedLedger = customerLedger.slice(startIndex, endIndex);
                          
                          return paginatedLedger.map((entry) => (
                            <tr key={entry.id} className="border-b hover:bg-gray-50">
                              <td className="px-4 py-2">
                                {new Date(entry.date).toLocaleDateString()}
                              </td>
                              <td className="px-4 py-2">
                                <span className={`px-2 py-1 rounded text-xs font-medium ${
                                  entry.transaction_type === 'credit' 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {entry.transaction_type === 'credit' ? 'CREDIT' : 'DEBIT'}
                                </span>
                              </td>
                              <td className="px-4 py-2">
                                <span className={entry.transaction_type === 'credit' ? 'text-green-600' : 'text-red-600'}>
                                  {entry.transaction_type === 'credit' ? '+' : '-'}₹{entry.amount.toLocaleString()}
                                </span>
                              </td>
                              <td className="px-4 py-2 text-sm">
                                {entry.description}
                              </td>
                              <td className="px-4 py-2 font-medium">
                                <span className={entry.balance >= 0 ? 'text-green-600' : 'text-red-600'}>
                                  ₹{Math.abs(entry.balance).toLocaleString()}
                                  {entry.balance >= 0 ? ' CR' : ' DR'}
                                </span>
                              </td>
                            </tr>
                          ));
                        })()}
                      </tbody>
                    </table>

                    {/* Pagination Controls */}
                    <div className="flex justify-between items-center">
                      <div className="text-sm text-gray-600">
                        Showing {((ledgerCurrentPage - 1) * ledgerPageSize) + 1} to {Math.min(ledgerCurrentPage * ledgerPageSize, customerLedger.length)} of {customerLedger.length} transactions
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setLedgerCurrentPage(prev => Math.max(prev - 1, 1))}
                          disabled={ledgerCurrentPage === 1}
                          className="px-3 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Previous
                        </button>
                        <span className="px-3 py-1">
                          Page {ledgerCurrentPage} of {Math.ceil(customerLedger.length / ledgerPageSize)}
                        </span>
                        <button
                          onClick={() => setLedgerCurrentPage(prev => Math.min(prev + 1, Math.ceil(customerLedger.length / ledgerPageSize)))}
                          disabled={ledgerCurrentPage >= Math.ceil(customerLedger.length / ledgerPageSize)}
                          className="px-3 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No transactions found for this customer.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;